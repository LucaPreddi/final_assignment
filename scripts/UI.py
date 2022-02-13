#!/usr/bin/env python3

# Importing the libraries.

import rospy
import os
import signal

# Implementing class with the colors.

class colorz:
	WHITE = '\033[95m'
	BLUE = '\033[94m'
	CYAN = '\033[96m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	END = '\033[0m'
	BOLD = '\033[1m'

# Declaring strings with some messages to display.

intro = """ 
""" + colorz.GREEN + colorz.BOLD + """
Hi! This is your User Interface """ + colorz.END + """
You can move the robot through three different modalities:"""

menu_msg = colorz.END + """
[1] """ + colorz.CYAN + """Insert and reach automatically your desired position.""" + colorz.END + """
[2] """ + colorz.CYAN + """Drive the robot using your keyboard. """ + colorz.END +"""
[3] """ + colorz.CYAN + """Drive the robot using your keyboard assisted by the program.""" + colorz.END + """
[4] """ + colorz.RED + """Quit the simulation.
"""

# Defining function switch(), this function will start the different
# modalities depending on what the user decides to choose. The variable
# boolprint is used to wait in the first modality the end of the task.

boolprint = False
def switch():
	global boolprint 
	print(menu_msg)

	if boolprint == True:
		print(colorz.YELLOW + colorz.BOLD + "Press [0] for canceling the target." + colorz.END)
		boolprint = False
	command = input(colorz.WHITE + 'Instert a command \n' + colorz.END)

	# Setting all the modalities idle.
	
	if command == "0":
		rospy.set_param('active', 0)
		print(colorz.GREEN + "Idle." + colorz.END)
		active_=rospy.get_param("/active")
		print(active_)

	# Starting the first modality, then asking the user which position he wants to reach.
	# Once the position is written we set the position on the parameters, these will be
	# read by the first modality.

	elif command == "1":

		rospy.set_param('active', 0)
		print(colorz.GREEN + "Modality 1 is active.")
		active_=rospy.get_param("/active")
		print(colorz.BLUE + colorz.BOLD + "Where do you want the robot to go?" + colorz.END)
		des_x_input = float(input(colorz.BOLD + colorz.BLUE +"Insert the desired x position: " + colorz.END))
		des_y_input = float(input(colorz.BOLD + colorz.BLUE +"Insert the desired y position: " + colorz.END))
		print(colorz.GREEN  + "Now we try to reach the position x = " + str(des_x_input) + " , y = " + str(des_y_input) + colorz.END)
		print(colorz.GREEN  + "The robot is moving towards your desired target!" + colorz.END)		
		rospy.set_param('des_pos_x', des_x_input)
		rospy.set_param('des_pos_y', des_y_input)
		rospy.set_param('active', 1)
		boolprint=True

	# Starting the second modality.

	elif command == "2":
		rospy.set_param('active', 2)
		print(colorz.GREEN + "Modality 2 is active." + colorz.END)
		active_ = rospy.get_param("/active")
	
	# Starting the third modality.

	elif command == "3":
		rospy.set_param('active', 3)
		print(colorz.GREEN + "Modality 3 is active." + colorz.END)
		active_=rospy.get_param("/active")

	# If we want to quit the program, we press 4.

	elif command == "4":
		print(colorz.YELLOW + colorz.BOLD + "Exiting..." + colorz.END)
		os.kill(os.getpid(), signal.SIGKILL)
	
	# If the user presses anything else, we want to quit the program.

	else:
		print(colorz.RED + "Wrong key!" + colorz.END)

# What we want now, is to call the functions created and printing the starting message.

def main():
	print(intro)
	while not rospy.is_shutdown():
		switch()

main()