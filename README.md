# RT1Assignment3
The second assignment of the Research Track 1 class regards the use of a robot simulator in ROS (Robot Operating System) and the programming of a really simple UI (User Interface) with 3 different modalities.

Installing and running
----------------------

The simulator requires ROS (Robot Operating System), which is a set of software libraries and tools that help you build robot applications. The simulator perfectly runs on the [Noetic Release of ROS](http://wiki.ros.org/noetic/Installation), I haven't tried the [ROS 2 release](https://docs.ros.org) yet, so let me know if it does actually work. 


The simulator requires __slam_gmapping__ package, so please install it before using the package here presented! [_Link to install slam_gmapping package._](http://wiki.ros.org/slam_gmapping)


The simulator requires __Gazebo and Rviz__, so please check that you have installed those two programs!


Anyway you can check every release of ROS in this [link](http://wiki.ros.org/ROS/Installation).

Another tool to be installed is the xterm interface. We use it to make the user experience more appreciatable, so run this command:
```bash
$ sudo apt-get install -y xterm
```
Once you have installed ROS and xterm, you should've even created a workspace where you can build up your packages. So, if you haven't still done it, download the package on GitHub and copy it in your `/src` folder. Then you should run:
```bash
$ roscore &
```
to __run ROS__ in your pc.
```bash
$ catkin_make
```
to __build the workspace__. Then, in order to refresh the package list, run:
```bash
$ rospack profile
```
Once you have installed ROS and the package, __run the following roslaunch__:
```bash
$ roslaunch final_assignment simulation.launch
```
__You should now see many different windows, 4 consoles gazebo and Rviz.__

Introduction
----------------------

__The aim of the project is to create a simulation of a robot with Gazebo and Rviz, in order to make the robot exploring the map. The simulation is like this:__

The circuit is the following:
<p align="center">
<img src="https://github.com/LucaPreddi/RT1Assignment2/blob/main/Images/MonzaCircuit.png" width="500" height="450">
</p>

The professor asked us to build the package by using __three different modalities__, which means three different behaviours of the robot. 
__We had to develop a software architecture for the control of the robot in the environment. The software will rely on the move_base and gmapping packages for localizing the robot and plan the motion.__
The architecture should be able to get the user request, and ___let the robot execute one of the following behaviors___
(depending on the user’s input):
1. Autonomously reach a x,y coordinate inserted by the user.
2. Let the user drive the robot with the keyboard.
3. Let the user drive the robot assisting them to avoid collisions.

Logic behind the code
----------------------

To satisfy the requests I decided to code 4 different nodes inside the package, the simulation is managed by the simulation which was provided by the professor, essentially __you have to install the slam_gmapping package.__ Here's the idea behind the communication of the nodes:

<p align="center">
<img src="https://github.com/LucaPredieri/RT1Assignment3/blob/main/Blank%20diagram.png" width="470" height="425">
</p>

As you can see it's an easy idea, but the implementation is not that easy! Anyway I will go through everything.

_Briefly description_

The user through the console of the UI node will decide the modality to run, after that the robot will start it's modality and will show on the consoles of the modalities the result of the task, wheter it was okay or if something is going wrong. Anyway, the most important part is to understand the usage of the modalities.

## Nodes and their logic

_Here I will explain each node code and tasks, to have a deeper description of the code, check the comments inside of it._
__DISCLAIMER__: here I will explain the nodes that I developed by myself, so please for more infos about the other nodes check the ROS wiki.

### UI node (final_assignment package)

The u
