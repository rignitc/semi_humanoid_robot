#!/usr/bin/env python
import rospy
#Importing int message: Used to send command to arduino
from std_msgs.msg import Int32
#Handling command line arguments
import sys
#Function to give direction
num = 0
def callback(data):
    global num
    num=data.data
    # print"callback called"

def move_arduino(directions):
    # print "In move_arduino"
    #rospy.init_node('arduino', anonymous=False)
    #The arduino is the topic in which we have to send direction messages
    # pub = rospy.Publisher('/directions', Int16, queue_size=10)
    rospy.loginfo("direction =%d",directions)
    #Publishing direction message
    pub.publish(directions)

def listener():
    global num
    rospy.Subscriber("/controller", Int32, callback)
    while not rospy.is_shutdown():
        # print "listener running"
        rate = rospy.Rate(10) # 10hz
        #Creating direction message instance
        direction = Int32()
        move_arduino(num)
        rate.sleep()

    # while not rospy.is_shutdown():
                
    #             rate.sleep()

    
if __name__ == '__main__':
    rospy.init_node('arduino')
    pub = rospy.Publisher('/directions', Int32, queue_size=10)
    # print "In main"
    try:
        #Providing moving direction through command line
       listener() 
    except rospy.ROSInterruptException:
        pass
