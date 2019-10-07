#!/usr/bin/env python
import rospy
from std_msgs.msg import String,Int32

def publish_int(value):
	value=int(value)
	pub_1.publish(value)
	rate.sleep()
def publish_string(value):
	pub_2.publish(value)
	rate.sleep()
def interpret(text):
	if text =="front":
		publish_int(8)
	elif text =="back":
		print "back"
		publish_int(2)
	elif text =="right":
		print "right"
		publish_int(6)
	elif text =="left":
		print "left"
		publish_int(4)
	elif text =="stop":
		print "stop"
		publish_int(5)
	elif text =="rotate":
		publish_int(10)
	else:
		publish_string(text)

def callback(data):
	text=data.data
	text=str(text)
	#print "sending %s"%text
	interpret(text)
	
				
				

def receiver():
	rospy.Subscriber('text_voice_writing',String,callback)
	print "received"
	rospy.spin()

if __name__=='__main__':

	rospy.init_node('text_interpreter',anonymous=True)
	pub_1=rospy.Publisher('controller',Int32, queue_size=10)
	pub_2=rospy.Publisher('chatter',String, queue_size=10)
	rate = rospy.Rate(10)
	try:
		print "try"
		receiver()
	except rospy.ROSInterruptException:
		pass
