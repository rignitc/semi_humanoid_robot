import  cv2
import numpy as np
import time

fpsLimit = 1
startTime = time.time()
stream = cv2.VideoCapture('videos/lunch_scene.mp4')
#stream.set(cv2.CAP_PROP_FPS, 
while True:
	ret, cap = stream.read()
	#stream.set(cv2.CAP_PROP_FPS,10)
	#fps = stream.get(cv2.CAP_PROP_FPS)	
	#print(fps)
	nowTime = time.time()
	if (int(nowTime - startTime)) > fpsLimit:
		cv2.imshow('image', cap)
		print(cap)
		startTime = time.time()
	cv2.waitKey(1)
	#time.sleep(25)
