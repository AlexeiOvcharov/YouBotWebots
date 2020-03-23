import sys, select, termios, tty
import rospy
class BaseController:

    def __init__(self, joints):
        self.msg = """
        Reading from the keyboard  and Publishing to Twist!
        ---------------------------
        Moving around:
           u    i    o
           j    k    l
           m    ,    .
        For Holonomic mode (strafing), hold down the shift key:
        ---------------------------
           U    I    O
           J    K    L
           M    <    >
        t : up (+z)
        b : down (-z)
        anything else : stop
        q/z : increase/decrease max speeds by 10%
        w/x : increase/decrease only linear speed by 10%
        e/c : increase/decrease only angular speed by 10%
        CTRL-C to quit
        """

        self.moveBindings = {
            'i':(1,0,0,0),
            'o':(1,0,0,-1),
            'j':(0,0,0,1),
            'l':(0,0,0,-1),
            'u':(1,0,0,1),
            ',':(-1,0,0,0),
            '.':(-1,0,0,1),
            'm':(-1,0,0,-1),
            'O':(1,-1,0,0),
            'I':(1,0,0,0),
            'J':(0,1,0,0),
            'L':(0,-1,0,0),
            'U':(1,1,0,0),
            '<':(-1,0,0,0),
            '>':(-1,-1,0,0),
            'M':(-1,1,0,0),
            't':(0,0,1,0),
            'b':(0,0,-1,0),
        }

        self.speedBindings = {
            'q':(1.1,1.1),
            'z':(.9,.9),
            'w':(1.1,1),
            'x':(.9,1),
            'e':(1,1.1),
            'c':(1,.9),
        }

        self.speed = 0.5
        self.turn = 1
        self.x = 0
        self.y = 0
        self.th = 0
        self.status = 0
        self.twist = [0, 0, 0]

        # Base parameters
        self.A = 74.87/1000     # Wheel width
        self.B = 100.0/1000     # Wheel diameter
        self.C = 471.0/1000     # Between from and rear wheels
        self.D = 300.46/1000    # Base width
        self.E = 28.0/1000      # Roll diameter
        self.slideRatio = 1

        self.joints = joints
        self.joints[0].setPosition(float('+inf'))
        self.joints[1].setPosition(float('+inf'))
        self.joints[2].setPosition(float('+inf'))
        self.joints[3].setPosition(float('+inf'))

        self.settings = termios.tcgetattr(sys.stdin)

        print(self.msg)
        print("currently:\tspeed %s\tturn %s " % (self.speed, self.turn))

    def getKey(self):
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key


    def vels(self):
        return "currently:\tspeed %s\tturn %s " % (self.speed, self.turn)

    def getTwist(self):
        try:
            key = self.getKey()
            if key in self.moveBindings.keys():
                self.x = self.moveBindings[key][0]
                self.y = self.moveBindings[key][1]
                self.th = self.moveBindings[key][3]
            elif key in self.speedBindings.keys():
                self.speed = self.speed * self.speedBindings[key][0]
                self.turn = self.turn * self.speedBindings[key][1]

                print(self.vels())
                if (self.status == 14):
                    print(self.msg)
                self.status = (self.status + 1) % 15
            else:
                self.x = 0
                self.y = 0
                self.th = 0
                if (key == 'Q'):
                    self.joints[0].setVelocity(0)
                    self.joints[1].setVelocity(0)
                    self.joints[2].setVelocity(0)
                    self.joints[3].setVelocity(0)
                    rospy.signal_shutdown('Out from nmode by Q')

            self.twist[0] = self.x*self.speed
            self.twist[1] = self.y*self.speed
            self.twist[2] = self.th*self.turn
            return

        except Exception as e:
            print(e)
            self.twist[0] = 0; self.twist[1] = 0; self.twist[2] = 0;

    def getMotorVelocities(self):
        velFromX = self.twist[2]/self.B
        velFromY = self.twist[1]/(self.B*self.slideRatio)
        velFromTheta = self.twist[0] * (self.C + self.D) / self.B

        wheelVelocities = [0, 0, 0, 0]
        wheelVelocities[0] =  velFromX + velFromY + velFromTheta
        wheelVelocities[1] = -velFromX - velFromY + velFromTheta
        wheelVelocities[2] =  velFromX - velFromY + velFromTheta
        wheelVelocities[3] = -velFromX + velFromY + velFromTheta

        return wheelVelocities;

    def rotateBaseMotors(self):

        self.getTwist()
        # print(self.twist)
        wheelVelocities = self.getMotorVelocities()

        resp1 = self.joints[0].setVelocity(wheelVelocities[0])
        resp2 = self.joints[1].setVelocity(wheelVelocities[1])
        resp3 = self.joints[2].setVelocity(wheelVelocities[2])
        resp4 = self.joints[3].setVelocity(wheelVelocities[3])
