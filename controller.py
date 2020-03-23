#!/usr/bin/python
import rospy
from teleop_twist_keyboard import BaseController

from std_msgs.msg import String
from webots_ros.srv import set_float

class Motor:
    def __init__(self, name):
        print(name + 'set_velocity')
        self.setPosition = rospy.ServiceProxy(name + 'set_position', set_float)
        self.setVelocity = rospy.ServiceProxy(name + 'set_velocity', set_float)


def model_name_callback(msg):
    global modelName, nameReader
    nameReader.unregister()

    modelName = msg.data
    print(modelName)

    baseJoints = []
    baseJoints.append(Motor('/{}/wheel1/'.format(modelName)))
    baseJoints.append(Motor('/{}/wheel2/'.format(modelName)))
    baseJoints.append(Motor('/{}/wheel3/'.format(modelName)))
    baseJoints.append(Motor('/{}/wheel4/'.format(modelName)))

    baseController = BaseController(baseJoints)

    while not rospy.is_shutdown():
        baseController.rotateBaseMotors()




if __name__=="__main__":
    modelName = ''

    rospy.init_node('teleop_twist_keyboard')
    nameReader = rospy.Subscriber("/model_name", String, model_name_callback)

    rospy.spin()
