#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
import os
flag = 0
list_greeted =[]
def callback(data):
	text=data.data
	text1=str(text)
	print ("text is :",text1)
	os.system("espeak hello")
	if len(text1) > 0 :
		if text1 in list_greeted:
			print('Nothing')
		else:
			if text1 == "Unknown":
				os.system("espeak I...don't...know...you...can...I...take...your...photo...")
				list_greeted.append(text1)
			else:
				os.system("espeak Hi...How....are...you?")
				os.system("espeak " +str(text1))			
				print(text1)
				list_greeted.append(text1)
		#flag = 1
		#else:
		#	os.system("espeak I...don't...know...you...can...I...take...your...photo...")
		#	flag = 0

def receiver():
	rospy.Subscriber('face_rec',String,callback)
	rospy.spin()

if __name__=='__main__':
	#flag = 0
	rospy.init_node('greet',anonymous=True)
	rate = rospy.Rate(10)
	try:
		receiver()
	except rospy.ROSInterruptException:
		pass
