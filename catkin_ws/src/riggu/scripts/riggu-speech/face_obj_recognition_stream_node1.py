#!/usr/bin/python3
from ctypes import *
import math
import random
import argparse
import cv2
import time
import rospy
from std_msgs.msg import String
import face_rec
fpsLimit = 12
startTime = time.time()

#argument parser to get input video files
ap = argparse.ArgumentParser()
#ap.add_argument("-i", "--input", required=True,
#	help="path to input video")
ap.add_argument("-o", "--output", type=str,
	help="path to output video")
args = vars(ap.parse_args())
#stream = cv2.VideoCapture(args["input"])
writer = None

def talker(hello_str):
	pub = rospy.Publisher('chatter', String, queue_size=100)
	rospy.init_node('talker', anonymous=True)
	rate = rospy.Rate(10) # 10hz
	while not rospy.is_shutdown():
		hello_str = hello_str #+ rospy.get_time()
		rospy.loginfo(hello_str)
		pub.publish(hello_str)
		rate.sleep()


def sample(probs):
	s = sum(probs)
	probs = [a/s for a in probs]
	r = random.uniform(0, 1)
	for i in range(len(probs)):
		r = r - probs[i]
		if r <= 0:
			return i
	return len(probs)-1

def c_array(ctype, values):
	arr = (ctype*len(values))()
	arr[:] = values
	return arr

class BOX(Structure):
	_fields_ = [("x", c_float),
				("y", c_float),
				("w", c_float),
				("h", c_float)]

class DETECTION(Structure):
	_fields_ = [("bbox", BOX),
				("classes", c_int),
				("prob", POINTER(c_float)),
				("mask", POINTER(c_float)),
				("objectness", c_float),
				("sort_class", c_int)]


class IMAGE(Structure):
	_fields_ = [("w", c_int),
				("h", c_int),
				("c", c_int),
				("data", POINTER(c_float))]

class METADATA(Structure):
	_fields_ = [("classes", c_int),
				("names", POINTER(c_char_p))]

	

lib = CDLL("/home/nvidia/darknet/libdarknet.so", RTLD_GLOBAL) ##replace it with path in pc
#lib = CDLL("libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)


def open_cam_rtsp(uri, width, height, latency):
	gst_str = ('rtspsrc location={} latency={} ! '
				'rtph264depay ! h264parse ! omxh264dec ! '
				'nvvidconv ! '
				'video/x-raw, width=(int){}, height=(int){}, '
				'format=(string)BGRx ! '
				'videoconvert ! appsink').format(uri, latency, width, height)
	return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

def open_cam_usb(dev, width, height):
	# We want to set width and height here, otherwise we could just do:
	#     return cv2.VideoCapture(dev)
	gst_str = ('v4l2src device=/dev/video{} ! '
				'video/x-raw, width=(int){}, height=(int){}, '
				'format=(string)RGB ! '
				'videoconvert ! appsink').format(dev, width, height)
	return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

def open_cam_onboard(width, height):
	# On versions of L4T prior to 28.1, add 'flip-method=2' into gst_str
	gst_str = ('nvcamerasrc ! '
				'video/x-raw(memory:NVMM), '
				'width=(int)2592, height=(int)1458, '
				'format=(string)I420, framerate=(fraction)30/1 ! '
				'nvvidconv ! '
				'video/x-raw, width=(int){}, height=(int){}, '
				'format=(string)BGRx ! '
				'videoconvert ! appsink').format(width, height)
	return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

def read_cam(cap):
	show_help = False
	full_scrn = False
	help_text = '"Esc" to Quit, "H" for Help, "F" to Toggle Fullscreen'
	font = cv2.FONT_HERSHEY_PLAIN
	_, img = cap.read() # grab the next image frame from camera
	#cv2.imshow(WINDOW_NAME, img)
	return img



def classify(net, meta, im):
	out = predict_image(net, im)
	res = []
	for i in range(meta.classes):
		res.append((meta.names[i], out[i]))
	res = sorted(res, key=lambda x: -x[1])
	return res

def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
	im = load_image(image, 0, 0)
	num = c_int(0)
	pnum = pointer(num)
	predict_image(net, im)
	dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
	num = pnum[0]
	flag = 0
	if (nms): do_nms_obj(dets, num, meta.classes, nms);
	res = []
	for j in range(num):
		for i in range(meta.classes):
			if dets[j].prob[i] > 0:
				b = dets[j].bbox
				flag = 1
				
				res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
	res = sorted(res, key=lambda x: -x[1])
	free_image(im)
	free_detections(dets, num)
	return res

def crop_image(image, box):
	px = (int)(box[0])			## px and py are the centre of the detection
	py = (int)(box[1])
	pw = (int)(box[2])			## pw and ph are width and height of the detection
	ph = (int)(box[3])
	if 2*px > pw and 2*py > ph:
		p_x = (int)(px-pw/2)
		p_y = (int)(py-ph/2)
		cropped_image = image[p_y:p_y+ph,p_x:p_x+pw]
	else:
		cropped_image = image
	#cropped_image = image[int(box[1]):int(box[3]),int(box[0]):int(box[2])]
	#print(p_x,p_y,pw,ph)
	#print("box:",box)
	print("values:", box)
	return cropped_image

def output(image, net, meta, re):			#define names clearly
	cv2.imwrite("predict.jpg", image)
	r = detect(net, meta, b"predict.jpg")
	print(r)
	#talker(r)
	if re == []:
		print("nothing detected")
	else:
		new_list = []
		new_list = re[2]
		px = (int)(new_list[0])			## px and py are the centre of the detection
		py = (int)(new_list[1])
		pw = (int)(new_list[2])			## pw and ph are width and height of the detection
		ph = (int)(new_list[3])
		p_x = (int)((2*px-pw)/2)
		p_y = (int)((2*py-ph)/2)
		name = re[0].decode("utf-8")
		#talker(name)
		image = cv2.rectangle(image,(p_x,p_y),(p_x+pw,p_y+ph),(0,255,0),3)   #(p_x+pw,p_y+ph) is opposite vertex of (p_x,p_y)
		p = p_y - 15 if p_y - 15 > 15 else p_y + 15
		cv2.putText(image, name, (px, p), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
	return image



path1 = b"/home/nvidia/darknet/cfg/yolov3-tiny.cfg"  ##replace these with paths in pc
path2 =  b"/home/nvidia/darknet/yolov3-tiny.weights"
re = []
if __name__ == "__main__":
	#net = load_net("cfg/densenet201.cfg", "/home/pjreddie/trained/densenet201.weights", 0)
	#im = load_image("data/wolf.jpg", 0, 0)
	#meta = load_meta("cfg/imagenet1k.data")
	#r = classify(net, meta, im)
	#print r[:10]
	net = load_net(path1,path2, 0)
	meta = load_meta(b"/home/nvidia/darknet/cfg/coco.data")
	cap = open_cam_usb(1,640,480)
	while(True):

		# ret,image = stream.read()
		ret = True
		image = read_cam(cap)
		cv2.imshow("image",image)
		pub = rospy.Publisher('chatter', String, queue_size=100)
		rospy.init_node('talker', anonymous=True)
		#rate = rospy.Rate(10) # 10hz
		#while not rospy.is_shutdown():
		#hello_str = hello_str #+ rospy.get_time()
		

		if not ret:
			break
		nowTime = time.time()
		time_elasped = nowTime - startTime
		if time_elasped > 1./fpsLimit:

			cv2.imwrite("predict.jpg", image)
			r = detect(net, meta, b"predict.jpg")
			#talker()
			if r == []:
				print()
			else:
				for re in r:
					image = output(image, net, meta, re)
			if writer is None and args["output"] is not None:
				fourcc = cv2.VideoWriter_fourcc(*"MJPG")
				writer = cv2.VideoWriter(args["output"], fourcc, 24,  (image.shape[1], image.shape[0]), True)
			#talker(name)	
			if writer is not None:
				writer.write(image)
			if len(re) > 0:
				for i in range(0, int(len(re)/3)):
					rospy.loginfo(str(re[3*i].decode("utf-8")))
					pub.publish(str(re[3*i].decode("utf-8")))
					if re[3*i].decode("utf-8") == "person":
						print("re3:", re[3*i+2])
						cropped_image = crop_image(image, re[3*i+2])
						cv2.imshow("cropped", cropped_image)
						cv2.waitKey(1)
						names = face_rec.face(cropped_image)
						print("names:",names)
			cv2.imshow("image", image)
			startTime = time.time()
		cv2.waitKey(1)

