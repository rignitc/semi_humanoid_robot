#!/usr/bin/env python3
import rospy
#Importing int message: Used to send command to arduino
from std_msgs.msg import Int32
#Handling command line arguments

def move_arduino(directions):
    rospy.init_node('joystick', anonymous=False)
    #The arduino is the topic in which we have to send direction messages
    pub = rospy.Publisher('/controller',Int32, queue_size=10)
    rate = rospy.Rate(10) # 10hz
    #Creating direction message instance
    direction = Int32()


    while not rospy.is_shutdown():
                direction=int(input('enter'))
                rospy.loginfo("direction =%d",direction)
                #Publishing direction message
                pub.publish(direction)
                #rate.sleep()
if __name__ == '__main__':
    try:
        #Providing moving direction through command line
       value=5
       move_arduino(int(value))
       
    except rospy.ROSInterruptException:
        pass
