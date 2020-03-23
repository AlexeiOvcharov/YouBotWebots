"""youbot_driver controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, Motor
from teleop_twist_keyboard import BaseController
from controller import Lidar

def arm_reset():
    armJoints[0].setPosition(1.0)
    armJoints[1].setPosition(1.57)
    armJoints[2].setPosition(-2.635)
    armJoints[3].setPosition(1.78)
    armJoints[4].setPosition(0.0)

def base_reset():
    baseJoints[0].setVelocity(0.0)
    baseJoints[1].setVelocity(0.0)
    baseJoints[2].setVelocity(0.0)
    baseJoints[3].setVelocity(0.0)

# create the Robot instance.
robot = Robot()

# Setup arm
armJointNames = ['arm1', 'arm2', 'arm3', 'arm4', 'arm5']
armJoints = [];
for name in armJointNames:
    armJoints.append(robot.getMotor(name))
    armJoints[-1].setVelocity(0.5)
arm_reset()

# Setup base
baseJointNames = ['wheel1', 'wheel2', 'wheel3', 'wheel4']
baseJoints = [];
for name in baseJointNames:
    baseJoints.append(robot.getMotor(name))
    baseJoints[-1].setPosition(float('+inf'))
    baseJoints[-1].setVelocity(0.0)
base_reset()

# Create BaseController
baseController = BaseController(baseJoints)

# Create Lidar
lidarName = 'Hokuyo URG-04LX-UG01'
lidar = Lidar(lidarName)
lidar.enable(30)
lidar.enablePointCloud()

print('Successfull start')

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getMotor('motorname')
#  ds = robot.getDistanceSensor('dsname')
#  ds.enable(timestep)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    baseController.rotateBaseMotors()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
