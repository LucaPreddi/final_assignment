#! /usr/bin/env python3

# Importing the libraries.

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf import transformations
from std_srvs.srv import *

# Implementing the class colorz, the class which assign the name 
# to the colors.

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	ORANGE = '\033[33m' 
	PURPLE  = '\033[35m'

# Implementing class with the colors.
# Creating message to display later.

msg = """ 
""" + bcolors.BOLD + """
This node makes the robot autonomously reach a x,y position inserted by the user on the UI interface.
It uses actionlib, which permits to us to make the code simplier and better.
""" +bcolors.ENDC + """
"""

# Assigning to local variables the data travelling around ROS' nodes.
# This part is crucial.

goal_msg = MoveBaseGoal()												# Action message
active_ = rospy.get_param('active')										# ROS poarameter to block/unlock the modality 
desired_position_x = rospy.get_param('des_pos_x')						# X desired coordinate 
desired_position_y = rospy.get_param('des_pos_y')						# Y desired coordinate 
client = actionlib.SimpleActionClient('/move_base', MoveBaseAction)		# Action client.
achieved = False														# Variable for defining if a goal was achieved or not.

# Defining ActionClient(), the function starts the communication with wait_for_server()
# The action client and server communicate over a set of topics, described in the actionlib protocol. 
# The action name describes the namespace naining these topics, and the action specification 
# message describes what messages should be passed along these topics. 

def ActionClient():
	global goal_msg
	global client
	client.wait_for_server()
	goal_msg.target_pose.header.frame_id = 'map'			
	goal_msg.target_pose.header.stamp = rospy.Time.now()	
	goal_msg.target_pose.pose.orientation.w = 1				

# Defining done_cb() function, this function updates when status value changes
# and it's the core of the action, because it changes the behaviour of the robot
# the n variable 

def done_cb(status, result):
	global client
	global achieved

	if status == 2:
		print(bcolors.FAIL + "Goal received a cancel request." + bcolors.ENDC)
		return
	if status == 3:
		print(bcolors.OKGREEN + bcolors.BOLD + "Goal achieved!" + bcolors.ENDC)
		achieved = True
		return
	if status == 4:
		print(bcolors.FAIL + bcolrs.BOLD + "Timeout expired. Goal aborted."  + bcolors.ENDC)
		return
	if status == 5:
		print(bcolors.FAIL + bcolrs.BOLD + "The goal was not accepted." + bcolors.ENDC)
		return
	if status == 6:
		print(bcolors.FAIL + bcolrs.BOLD + "The goal received a cancel request when he didn't finished the task."+ bcolors.ENDC)
		return
	if status == 8:
		print(bcolors.FAIL + bcolrs.BOLD + "The goal received a cancel request before it started executing. "+ bcolors.ENDC)
		return

# No-parameter callback that gets called on transitions to Active.

def active_cb():
	k=1

# Callback that gets called whenever feedback for this goal is received. Takes one parameter: the feedback. 

def feedback_cb(feedback):
	k=1

# SetGoal() is used to set the goal data in the goal_msg which will be published.
# Sends a goal to the ActionServer, and also registers callbacks.
# If a previous goal is already active when this is called. We simply forget about 
# that goal and start tracking the new goal. No cancel requests are made.

def SetGoal(x, y):
	global goal_msg
	global client
	goal_msg.target_pose.pose.position.x = x
	goal_msg.target_pose.pose.position.y = y
	client.send_goal(goal_msg, done_cb, active_cb, feedback_cb)

# UpdatingVariables() is used to keep update the three parameters crucial to the script,
# active_, desired_position_x, desired_position_y.

def UpdatingVariables():
	global desired_position_x, desired_position_y, active_
	active_ = rospy.get_param('active')
	desired_position_x = rospy.get_param('des_pos_x')
	desired_position_y = rospy.get_param('des_pos_y')

# Defining main() function.

def main():

	global client
	global goal_msg
	global achieved

	rospy.init_node('go_to_desired_pos') # Init node

	# Running the ActionClient() function to start the communication with the action.

	ActionClient()

	# Boolprint used in order to know if the previous state was printable.

	boolprint = 0
	print(msg) 

	while (1):
		
		# Updating the variables (including active_).

		UpdatingVariables()

		# If active_ is turned to 1 we procede with the task of the process.

		if active_==1:
			
			# If the prevoius state was Idle then we can set a new goal

			if boolprint == 1:
				print(bcolors.OKGREEN + bcolors.BOLD + "The robot is moving towards your desired target. " + bcolors.ENDC)
				SetGoal(desired_position_x, desired_position_y)	# Here we decide to set a new goal.
				boolprint = 0	# If this modality will be blocked, then we have to be put in idle.

		# If we are in Idle state but a goal was not achieved we need to cancel the goal.
		# If active_ is turned to 0 we can idle the process and wait until the
		# first modality is asked by the user. In any case, we want to cancel 
		# the goal asked by the user.

		else:

			# If the robot is idle forced by the user we do this:

			if boolprint == 0 and achieved == False:
				print(bcolors.OKBLUE + "Modality 1 is currently in idle state. \n" + bcolors.ENDC)
				client.cancel_goal()
				boolprint = 1

			# If the robot has achieved the goal.
			if achieved == True:
				boolprint = 1
				achieved = False


if __name__ == '__main__':
    main()