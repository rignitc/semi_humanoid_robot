#!/usr/bin/env python
import rospy 
from std_msgs.msg import String

def publish_text(value):
	pub.publish(value)
	


def command():
	rospy.init_node('text_cmd',anonymous=False)
	rate = rospy.Rate(10) # 10hz
	while True:
		text=str(raw_input("Enter the text command to the robot :"))
		if text=='quit':
			break
		text=text.lower()
		publish_text(text)
		rate.sleep()
		

if __name__=='__main__':
	try:
		pub=rospy.Publisher('text_voice_writing',String, queue_size=10)
		command()
	except rospy.ROSInterruptException:
		pass



