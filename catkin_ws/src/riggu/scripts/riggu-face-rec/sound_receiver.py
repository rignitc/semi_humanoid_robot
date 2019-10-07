#!/usr/bin/env python
import rospy
import time
from std_msgs.msg import String
from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient
dummy=""
def callback(data):
    rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data.data)
    name_string=data.data
    global dummy
    if dummy!=name_string:
	soundhandle = SoundClient()
	rospy.sleep(1)
    	voice = 'voice_kal_diphone'
        volume = 2.0
	time.sleep(2)
        soundhandle.say("hi "+name_string, voice, volume)
	#time.sleep(1)
	#soundhandle.say("hi are you", voice, volume)
    	rospy.sleep(1)
    	dummy=name_string
    	
	
    
    
    

def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # name are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('sound_receiver', anonymous=True)

    rospy.Subscriber('sound_string', String, callback)
    

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
      listener()
