#! /usr/bin/env python3

# import ros and other libraries.

import rospy
from sensor_msgs.msg import LaserScan
from move_base_msgs.msg import MoveBaseActionGoal
from actionlib_msgs.msg import GoalID 
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from tf import transformations
from std_srvs.srv import *
import time
import math

# Implementing class with the colors.

class bcolors:
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

# Creating message to display later.

msg = """ 
""" + bcolors.BOLD + """
This node makes the robot autonomously reach a x,y position inserted by the user on the UI interface.
The user x,y inputs are published on the 'move_base/goal' topic, and 
therefore the robot is going to plan the path through the Dijkstra's algorithm. 
""" +bcolors.ENDC + """
"""

# Assigning to local variables the data travelling around ROS' nodes.
# This part is crucial.

goal_msg = MoveBaseActionGoal()
goal_cancel = GoalID()
position_ = Point()
my_timer = 0
goal_msg.goal.target_pose.header.frame_id = 'map'
goal_msg.goal.target_pose.pose.orientation.w = 1
active_ = rospy.get_param('active')
desired_position_x = rospy.get_param('des_pos_x')
desired_position_y = rospy.get_param('des_pos_y')

# Defining functions called in the main().

# SetGoal() is used to set the goal data in the goal_msg which will be published.

def SetGoal(x, y):
	goal_msg.goal.target_pose.pose.position.x = x
	goal_msg.goal.target_pose.pose.position.y = y
	pub_goal.publish(goal_msg)

# CallBackOdometry() is used to pass the position of the robot to a local variable (of the 
# modality1.py script).

def CallBackOdometry(msg):
	global position_
	position_ = msg.pose.pose.position

# UpdatingVariables() is used to keep update the three parameters crucial to the script,
# active_, desired_position_x, desired_position_y.

def UpdatingVariables():
	global desired_position_x, desired_position_y, active_
	active_ = rospy.get_param('active')
	desired_position_x = rospy.get_param('des_pos_x')
	desired_position_y = rospy.get_param('des_pos_y')

# Calling a timeout after which the target stops to reach the goal, this is evaluated
# for those cases in which the robot cannot reach the goal.

def CallbackTimeout(event):
	if active_==1:
		print (bcolors.FAIL + "Timer has finished, the robot couldn't reach the position." + bcolors.ENDC)
		print(bcolors.FAIL + bcolors.BOLD + "Target canceled! Set again the first modality to set a new goal.\n" + bcolors.ENDC)
		rospy.set_param('active', 0)

# Defining main() function.

def main():

	global pub_vel 
	global pub_goal
	
	boolprint = 0
	
	# Initializing node and publishing goal, velocity and the parameter to cancel the goal value.
	
	rospy.init_node('modality1')
	pub_goal = rospy.Publisher('/move_base/goal', MoveBaseActionGoal, queue_size = 1)
	pub_cancel_goal = rospy.Publisher('/move_base/cancel', GoalID, queue_size = 1)
	pub_vel = rospy.Publisher('/cmd_vel', Twist, queue_size = 1)

	# Publishing goal_msg (MoveBaseActionGoal()).

	pub_goal.publish(goal_msg)
	
	# Subscribing to odomery data of the robot.
	
	sub_odom = rospy.Subscriber('/odom', Odometry, CallBackOdometry)
	
	# Looping the while with 10 Hz.
	
	rate = rospy.Rate(10)
	print(msg)
	while (1):
		
		UpdatingVariables()	# Updating the variables (including active_).

		# If active_ is turned to 0 we can idle the process and wait until the
		# first modality is asked by the user. In any case, we want to cancel 
		# the goal asked by the user.

		if active_ == 0:
			
			if boolprint == 0:
				print(bcolors.OKBLUE + bcolors.BOLD + "\nModality 1 is currently in idle state.\n" + bcolors.ENDC)
				pub_cancel_goal.publish(goal_cancel)
				boolprint = 1

		# If active_ is turned to 1 we procede with the task of the process.

		elif active_ == 1:
			if boolprint == 1:
				print(bcolors.OKGREEN + "The robot is moving towards your desired target!\n" + bcolors.ENDC)
				rospy.Timer(rospy.Duration(100),CallbackTimeout) # Starting the timer to make sure robot doesn't work endlessly.
				SetGoal(desired_position_x, desired_position_y) # Setting the goal of the robot.
				boolprint = 0

			# If the target is really close to the robot we say that we reached the destination.

			if abs(desired_position_x-position_.x) <= 0.5 and abs(desired_position_y-position_.y) <= 0.5:
				print(bcolors.OKGREEN + bcolors.UNDERLINE + bcolors.BOLD + "Target reached\n" + bcolors.ENDC)
				rospy.set_param('active', 0) # Then, we set active parameter to 0 to let the user decide what to do.

		rate.sleep()

# Calling main() function.

if __name__ == '__main__':
    main()
