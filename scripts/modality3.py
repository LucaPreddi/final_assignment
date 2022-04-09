#!/usr/bin/env python3

"""
.. module:: Modality3
 :platform: Unix
 :synopsis: Module for the second modality.

.. moduleauthor:: Luca Predieri <luca.predieri2018@gmail.com>
 
This code is just the already existing teleop_twist_keyboard package on ROS. Some of the code has been modified in  order to incorporate
the script with the final_assignment package. Some code won't be commented as gar as you can check the ROS wiki package of it by googling it.
Anyway, here's the link for getting deeper in the code: http://wiki.ros.org/teleop_twist_keyboard
The dictionary ``moveBindings`` will have some features popped out because when the robot is close to the walls. This permits to the user to avoid colliding with the walls.

"""

# Importing the libraries.

from __future__ import print_function
import threading
from sensor_msgs.msg import LaserScan
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy
from geometry_msgs.msg import Twist
import time
from std_srvs.srv import *
import sys, select, termios, tty

# Implementing class with the colors.

class colorz:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'
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
""" + colorz.BOLD +"""
This node makes the robot move with some keys, here's the list, enjoy!
Be careful! when you're close to walls it is gonna stop.
---------------------------
""" + colorz.END + colorz.BOLD + """
Moving around:
        i     
   j    k    l

""" + colorz.END + colorz.BOLD +"""
q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
""" + colorz.END + """

"""

# Checking if left right or straight is okay (if there's is a wall).

ok_left = True
ok_right = True
ok_straight = True

# This structure is really important and it's a dictionary.
# Dictionaries are Python’s implementation of a data struc-
# ture that is more generally known as an associative arra- 
# y. A dictionary consists of a collection of key-value pa-
# irs. Each key-value pair maps the key to its associated 
# value. Here what we want to map is how the robot moves i-
# n the space.

moveBindings = {
        'i':(1,0,0,0),
        'j':(0,0,0,1),
        'l':(0,0,0,-1),
        'k':(-1,0,0,0),
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

    def my_stop(self):
        twist = Twist()
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        # Publish.
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
    """
    Function to get the input from the keyboard without having the need to wait for the user to press enter.
    
    Args:
     key_timeout
    Returns:
     the k
    """
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], key_timeout)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

# Defining the callback function laser, so we can always check if around
# robot (in front, left and right) there's a wall. The algorithm is the 
# same as in the first assignment.

def CallbackLaser(msg):
    """
    Function to check if some wall is close to the robot.
    
    Args:
     message from the odometry of the robot
    """
    global ok_left
    global ok_right
    global ok_straight

    right = min(min(msg.ranges[0:143]), 1)
    front = min(min(msg.ranges[288:431]), 1)
    left = min(min(msg.ranges[576:719]), 1)

    if right != 1.0:
        ok_right = False
    else:
        ok_right = True

    if front != 1.0:
        ok_straight = False
    else:
        ok_straight = True

    if left != 1.0:
        ok_left = False
    else:
        ok_left = True

# Disabling the commands by popping from the dictionary in order to
# not let the robot moving towards the walls.

def pop_it(dictionary):
    """
    Function to pop the key from the dictionary. As you can see it's pretty intuitive, because depending by the position of the wall we
    pop some precise keys.
    
    Args:
     dictionary
    """
    global ok_left
    global ok_right
    global ok_straight

    if not ok_straight and not ok_right and not ok_left:
        popped1 = dictionary.pop('i')
        popped2 = dictionary.pop('j')
        popped3 = dictionary.pop('l')
        print(colorz.RED  + "Command 'i' disabled." + colorz.END, end="\r")
        print(colorz.RED + "Command 'j' disabled." + colorz.END , end="\r")
        print(colorz.RED + "Command 'l' disabled." + colorz.END , end="\r")
    elif not ok_left and not ok_straight and ok_right:
        popped1 = dictionary.pop('i')
        popped2 = dictionary.pop('j')
        print(colorz.RED + "Command 'i' disabled." + colorz.END , end="\r")
        print(colorz.RED + "Command 'j' disabled." + colorz.END , end="\r")
    elif ok_left and not ok_straight and not ok_right:
        popped1 = dictionary.pop('i')
        popped2 = dictionary.pop('l')
        print(colorz.RED + "Command 'i' disabled." + colorz.END , end="\r")
        print(colorz.RED + "Command 'l' disabled." + colorz.END , end="\r")
    elif not ok_left and ok_straight and not ok_right:
        popped1 = dictionary.pop('l')
        popped2 = dictionary.pop('j')
        print(colorz.RED + "Command 'l' disabled." + colorz.END , end="\r")
        print(colorz.RED + "Command 'j' disabled." + colorz.END , end="\r")
    elif ok_left and not ok_straight and ok_right:
        popped1 = dictionary.pop('i')
        print(colorz.RED + "Command 'i' disabled." + colorz.END , end="\r")
    elif not ok_left and ok_straight and ok_right:
        popped1 = dictionary.pop('j')
        print(colorz.RED + "Command 'j' disabled." + colorz.END , end="\r")
    elif ok_left and ok_straight and not ok_right:
        popped1 = dictionary.pop('l')
        print(colorz.RED + "Command 'l' disabled." + colorz.END , end="\r")

def main():
    """
    The main here is really important because as the different input arrives it changes the key moving the robots.
    As the other two modalities, we have again ``active`` which permits the user to use the modality as he wants.
    As you could see, the modality 1 and the modality 2 are pretty equal, but here's the difference, when the robot is close to a wall,
    we pop the keys in the dictionary permitting the robot to move towards the robot. 

    """


if __name__=="__main__":

    boolprint = 1
    rospy.init_node('Modality3')
    active_=rospy.get_param("/active")
    settings = termios.tcgetattr(sys.stdin)
    speed = rospy.get_param("~speed", 0.5)
    turn = rospy.get_param("~turn", 1.0)
    repeat = rospy.get_param("~repeat_rate", 0.0)
    key_timeout = rospy.get_param("~key_timeout", 0.1)
    sub = rospy.Subscriber('/scan', LaserScan, CallbackLaser)
    if key_timeout == 0.0:
        key_timeout = None

    pub_thread = PublishThread(repeat)

    x = 0
    y = 0
    z = 0
    th = 0
    status = 0

    rate = rospy.Rate(5)
    pub_thread.wait_for_subscribers()
    pub_thread.update(x, y, z, th, speed, turn)

    # Creating moveBindings_copy dictionary in order to change
    # the user commands.

    moveBindings_copy = {}
    print(msg)

    while(1):

        # This instruction is really important because it's updating
        # the moveBindings_copy. If there wasn't this instruction, 
        # the robot would have some commands always disabled.

        moveBindings_copy = moveBindings.copy()
        active_ = rospy.get_param('active')

        if active_ == 3:

            # Advising the user that the modality 3 is on.

            if boolprint == 0:
                print(colorz.BOLD + colorz.GREEN + "You can start using this modality!\n" + colorz.END)
                boolprint = 1

            # Getting the key and popping the command in the dictionary.
            # The moveBindings_copy dictionary is the one we pass to the robot
            # but every loop gets the value of the original dictionary in orde
            # to be always updated.

            key = getKey(key_timeout)
            pop_it(moveBindings_copy)

            if key in moveBindings_copy.keys():

                x = moveBindings_copy[key][0] 
                y = moveBindings_copy[key][1]
                z = moveBindings_copy[key][2]
                th = moveBindings_copy[key][3]

            elif key in speedBindings.keys():

                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]
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

        # If the modality is disabled we advise the user.

        else:
            if boolprint == 1:
                pub_thread.my_stop() 
                print(colorz.BLUE + colorz.BOLD + "\nModality 3 is currently in idle state.\n" + colorz.END)
            boolprint = 0

        rate.sleep()