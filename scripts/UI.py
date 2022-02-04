#!/usr/bin/python3

# import ros and other libraries.

import rospy
import os
import signal

# Implementing class with the colors.

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

# Declaring strings with some messages to display.

intro = """ 
""" + bcolors.OKGREEN + bcolors.BOLD + """
Hi! This is your User Interface """ + bcolors.ENDC + bcolors.UNDERLINE + """
You can move the robot through three different modalities:"""

menu_msg = bcolors.ENDC + """
[1] """ + bcolors.OKCYAN + """Insert and reach automatically your desired position.""" + bcolors.ENDC + """
[2] """ + bcolors.OKCYAN + """Drive the robot using your keyboard. """ + bcolors.ENDC +"""
[3] """ + bcolors.OKCYAN + """Drive the robot using your keyboard assisted by the program.""" + bcolors.ENDC + """
[4] """ + bcolors.FAIL + """Quit the simulation.
"""

# Defining function interpreter(), this function will start the different
# modalities depending on what the user decides to choose. The variable
# flag is used to wait in the first modality the end of the task.

flag = False
def interpreter():
	global flag 
	print(menu_msg)

	if flag == True:
		print(bcolors.WARNING + bcolors.BOLD + "Press [0] for canceling the target." + bcolors.ENDC)
		flag = False
	command = input(bcolors.HEADER + 'Instert a command \n' + bcolors.ENDC)

	# Setting all the modalities idle.
	
	if command == "0":
		rospy.set_param('active', 0)
		print(bcolors.OKGREEN + "Idle." + bcolors.ENDC)
		active_=rospy.get_param("/active")
		print(active_)

	# Starting the first modality, then asking the user which position he wants to reach.
	# Once the position is written we set the position on the parameters, these will be
	# read by the first modality.

	elif command == "1":

		rospy.set_param('active', 0)
		print(bcolors.OKGREEN + bcolors.UNDERLINE + "Modality 1 is active.")
		active_=rospy.get_param("/active")
		print(bcolors.OKBLUE + bcolors.BOLD + "Where do you want the robot to go?" + bcolors.ENDC)
		des_x_input = float(input(bcolors.BOLD + bcolors.OKBLUE +"Insert the desired x position: " + bcolors.ENDC))
		des_y_input = float(input(bcolors.BOLD + bcolors.OKBLUE +"Insert the desired y position: " + bcolors.ENDC))
		print(bcolors.OKGREEN  + "Now we try to reach the position x = " + str(des_x_input) + " , y = " + str(des_y_input) + bcolors.ENDC)
		print(bcolors.OKGREEN  + "The robot is moving towards your desired target!" + bcolors.ENDC)		
		rospy.set_param('des_pos_x', des_x_input)
		rospy.set_param('des_pos_y', des_y_input)
		rospy.set_param('active', 1)
		flag=True

	# Starting the second modality.

	elif command == "2":
		rospy.set_param('active', 2)
		print(bcolors.OKGREEN + "Modality 2 is active." + bcolors.ENDC)
		active_ = rospy.get_param("/active")
	
	# Starting the third modality.

	elif command == "3":
		rospy.set_param('active', 3)
		print(bcolors.OKGREEN + "Modality 3 is active." + bcolors.ENDC)
		active_=rospy.get_param("/active")

	# If we want to quit the program, we press 4.

	elif command == "4":
		print(bcolors.WARNING + bcolors.BOLD + "Exiting..." + bcolors.ENDC)
		os.kill(os.getpid(), signal.SIGKILL)
	
	# If the user presses anything else, we want to quit the program.

	else:
		print(bcolors.FAIL + "Wrong key!" + bcolors.ENDC)

# What we want now, is to call the functions created and printing the starting message.

def main():
	print(intro)
	while not rospy.is_shutdown():
		interpreter()

main()