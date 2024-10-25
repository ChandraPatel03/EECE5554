#!/usr/bin/env python

import rospy
from std_msgs.msg import String

def callback(data):
    reversed_data = data.data[::-1]
    rospy.loginfo(rospy.get_caller_id() + ' I heard: %s', reversed_data)

def listener():

    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber('chatter', String, callback)

    rospy.spin()

if __name__ == '__main__':
    listener()

