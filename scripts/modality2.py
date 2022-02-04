#!/usr/bin/env python3

from __future__ import print_function
import threading
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy
from geometry_msgs.msg import Twist
import sys, select, termios, tty

# Implementing class with the colors.

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

#################### READ ME PLEASE! ####################
# This code is just the already existing teleop_twist_- #
# keyboard package on ROS. Some of the code has been m- #
# odified in order to incorporate the script with the   #
# final_assignment package. Some code won't be comment- #
# ed as far as you can check the ROS wiki package of t- #
# he package by googling it.                            #
# Anyway here's the link for getting deeper in the cod- #
# e: http://wiki.ros.org/teleop_twist_keyboard          #
#########################################################

msg = """ 
""" + bcolors.BOLD +"""
Reading from the keyboard and Publishing to Twist!

---------------------------

""" + bcolors.ENDC + bcolors.BOLD + """
Moving around:
   u    i    o
   j    k    l
   m    ,    .

""" + bcolors.ENDC + bcolors.BOLD + """
For Holonomic mode (strafing), hold down the shift key:
---------------------------
   U    I    O
   J    K    L
   M    <    >

t : up (+z)
b : down (-z)
""" + bcolors.ENDC + bcolors.BOLD + """
anything else : stop
""" + bcolors.ENDC + bcolors.BOLD +"""
q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
"""+ bcolors.ENDC +""" 

"""

# This structure is really important and it's a dictionary.
# Dictionaries are Python’s implementation of a data struc-
# ture that is more generally known as an associative arra- 
# y. A dictionary consists of a collection of key-value pa-
# irs. Each key-value pair maps the key to its associated 
# value. Here what we want to map is how the robot moves i-
# n the space.

moveBindings = {
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

speedBindings={
        'q':(1.1,1.1),
        'z':(.9,.9),
        'w':(1.1,1),
        'x':(.9,1),
        'e':(1,1.1),
        'c':(1,.9),
    }

# Defining PublishingThread() class with its relative methods.

class PublishThread(threading.Thread):
    def __init__(self, rate):

        super(PublishThread, self).__init__()
        self.publisher = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.th = 0.0
        self.speed = 0.0
        self.turn = 0.0
        self.condition = threading.Condition()
        self.done = False

        # Set timeout to None if rate is 0 (causes new_message to wait forever
        # for new data to publish)

        if rate != 0.0:
            self.timeout = 1.0 / rate
        else:
            self.timeout = None

        self.start()

    def wait_for_subscribers(self):
        i = 0
        while not rospy.is_shutdown() and self.publisher.get_num_connections() == 0:
            if i == 4:
                print("Waiting for subscriber to connect to {}".format(self.publisher.name))
            rospy.sleep(0.5)
            i += 1
            i = i % 5
        if rospy.is_shutdown():
            raise Exception("Got shutdown request before subscribers connected")

    def update(self, x, y, z, th, speed, turn):
        self.condition.acquire()
        self.x = x
        self.y = y
        self.z = z
        self.th = th
        self.speed = speed
        self.turn = turn

        # Notify publish thread that we have a new message.

        self.condition.notify()
        self.condition.release()

    def stop(self):
        self.done = True
        self.update(0, 0, 0, 0, 0, 0)
        self.join()

    # We need our function to stop the robot because we have
    # to publish it.

    def robot_stop(self):
        twist = Twist()
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        self.publisher.publish(twist)

    def run(self):
        twist = Twist()
        while not self.done:
            self.condition.acquire()

            # Wait for a new message or timeout.

            self.condition.wait(self.timeout)

            # Copy state into twist message.

            twist.linear.x = self.x * self.speed
            twist.linear.y = self.y * self.speed
            twist.linear.z = self.z * self.speed
            twist.angular.x = 0
            twist.angular.y = 0
            twist.angular.z = self.th * self.turn

            self.condition.release()

            # Publish.

            self.publisher.publish(twist)

        # Publish stop message when thread exits.

        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        self.publisher.publish(twist)

# Defining getKey, with which we'll get the input from the keyboard.

def getKey(key_timeout):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], key_timeout)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def vels(speed, turn):
    return "currently:\tspeed %s\tturn %s \n" % (speed,turn)

if __name__=="__main__":

    # Starting boolprint to 1 to print the first infos.

    boolprint = 1

    rospy.init_node('my_teleop_twist_kb')
    settings = termios.tcgetattr(sys.stdin)
    speed = rospy.get_param("~speed", 0.5)
    turn = rospy.get_param("~turn", 1.0)
    repeat = rospy.get_param("~repeat_rate", 0.0)
    key_timeout = rospy.get_param("~key_timeout", 0.1)

    if key_timeout == 0.0:
        key_timeout = None

    pub_thread = PublishThread(repeat)

    x = 0
    y = 0
    z = 0
    th = 0
    status = 0

    pub_thread.wait_for_subscribers()
    pub_thread.update(x, y, z, th, speed, turn)

    # Printing some informations and user interfaces commands.

    print(msg)
    print(vels(speed,turn))

    # Looping the process part.

    while(1):

        # Printing one time the idle state.

        if boolprint == 1:
            pub_thread.robot_stop() 
            print(bcolors.BOLD + bcolors.OKBLUE + "Modality 2 is currently in idle state.\n" + bcolors.ENDC)
            boolprint = 0

        # If the modality 2 is active, we want to procede with the task.

        while(rospy.get_param("/active") == 2):

            # Printing informations.

            if boolprint == 0:
                print(bcolors.BOLD + bcolors.OKGREEN + "You can start using this modality!\n" + bcolors.ENDC)
                boolprint = 1

            # Getting input and assigning the key to the output.

            key = getKey(key_timeout)
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                y = moveBindings[key][1]
                z = moveBindings[key][2]
                th = moveBindings[key][3]
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]

                print(vels(speed,turn))
                if (status == 14):
                    print(msg)
                status = (status + 1) % 15
            else:

                # Skip updating cmd_vel if key timeout and robot already
                # stopped.

                if key == '' and x == 0 and y == 0 and z == 0 and th == 0:
                    continue
                x = 0
                y = 0
                z = 0
                th = 0
                if (key == '\x03'):
                    break
            pub_thread.update(x, y, z, th, speed, turn)