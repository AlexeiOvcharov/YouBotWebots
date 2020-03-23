from controller import Keyboard

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
            '73':(1,0,0,0),
            '79':(1,0,0,-1),
            '74':(0,0,0,1),
            '76':(0,0,0,-1),
            '85':(1,0,0,1),
            '44':(-1,0,0,0),
            '46':(-1,0,0,1),
            '77':(-1,0,0,-1),
            '65615':(1,-1,0,0),
            '65609':(1,0,0,0),
            '65610':(0,1,0,0),
            '65612':(0,-1,0,0),
            '65621':(1,1,0,0),
            '65596':(-1,0,0,0),
            '65598':(-1,-1,0,0),
            '65613':(-1,1,0,0),
            '84':(0,0,1,0),
            '66':(0,0,-1,0),
        }

        self.speedBindings = {
            '81':(1.1,1.1),
            '90':(.9,.9),
            '87':(1.1,1),
            '88':(.9,1),
            '69':(1,1.1),
            '67':(1,.9),
        }

        self.keyboard = Keyboard()
        self.keyboard.enable(32)

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

        print(self.msg)
        print("currently:\tspeed %s\tturn %s " % (self.speed, self.turn))

    def getKey(self):
        key = self.keyboard.getKey()
        return str(key)


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
        #print(self.twist)
        wheelVelocities = self.getMotorVelocities()

        self.joints[0].setVelocity(wheelVelocities[0])
        self.joints[1].setVelocity(wheelVelocities[1])
        self.joints[2].setVelocity(wheelVelocities[2])
        self.joints[3].setVelocity(wheelVelocities[3])
