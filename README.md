# RT1Assignment3
The second assignment of the Research Track 1 class regards the use of a robot simulator in ROS (Robot Operating System) and the programming of a really simple UI (User Interface) with 3 different modalities.
Sphinx Documentation: https://lucapredieri.github.io/DiscoveryRobotROS/

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

<p align="center">
<img src="https://github.com/LucaPredieri/RT1Assignment3/blob/main/Schermata%202022-02-12%20alle%2019.57.13.png" width="564" height="254">
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

The UI node is a super easy node because it is used only to set the ROS parameter s travelling through the nodes. The most important one is the integer ```active``` which is the one dedicated to the modality of the robot. The other two are the desired positions which are useful only for the first modality. 

Essentially this is the pseudocoude behind my idea:

```
def switch():
	command = input
	if command == "0":
    Reset the robot to idle state and cancel the goal.
    
	elif command == "1":
    Start the first modality.

	elif command == "2":
    Start the second modality.
    
	elif command == "3":
    Start the third modality.
    
	elif command == "4":
    Quit the program.
    
	else:
    Print: "Wrong key!"
```

Here's a screenshot of the xterm console:

<p align="center">
<img src="https://github.com/LucaPredieri/RT1Assignment3/blob/main/Schermata%202022-02-13%20alle%2000.38.05.png" width="485" height="356">
</p>

### Modality 1 node (final_assignment package)

In the modality 1 the robot has to reach by itself a goal sent by the user in the UI node.

The UI node is the most interesting one because is based on ROSAction, all the magic takes place with the line:

```python
client = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
```

Thanks to this [wiki.ros page](http://wiki.ros.org/actionlib_tutorials/Tutorials/Writing%20a%20Simple%20Action%20Client%20%28Python%29) I could develop a good action with its functions ```done_cb()```, ```active_cb```, ```feedback_cb```. 
If you want to get deep into ROSaction check out this video:

[![Everything Is AWESOME](https://github.com/LucaPredieri/RT1Assignment3/blob/main/Schermata%202022-02-13%20alle%2015.47.41.png)](https://www.youtube.com/watch?v=aS9zubUpSI8)

Then, we have the function ```ActionClient()```, __the function starts the communication with wait_for_server(). The action client and server communicate over a set of topics, described in the actionlib protocol.  The action name describes the namespace naining these topics, and the action specification message describes what messages should be passed along these topics. __

The ```main()``` function takes the aim of the modality. First of all it loops, then we update the variables (containing the status of the modality and the position informations) and the code understands the behaviour of the robot _status_ thanks to the action.

The program has a control which permits to put the robot in idle state in the case the robot itself cannot reach a position (for example out of the maze). 

Here's a screenshot of the xterm console:

<p align="center">
<img src="https://github.com/LucaPredieri/RT1Assignment3/blob/main/Schermata%202022-02-13%20alle%2000.39.40.png" width="485" height="356">
</p>

### Modality 2 node (final_assignment package)

__The second modality is the one dedicate to the movement of the robot using the keyboard, I decided to simply use the following control table:__

| Direction   |      key      |
|----------|:-------------:|
| Straight |  'i' |
| Right |    'l'   |
| Left | 'j' |
| Back | 'k' |

The logic of the code is really simple, because I decided to use the already existing code of the package ___teleop_twist_keyboard___ the code, is open to be realaborated on their github repo, here's the [link](http://wiki.ros.org/teleop_twist_keyboard), as you can see it's pretty easy and what I've done is really simple.

Anyway I realaborated the code by using the paramater ```active``` because we want this modality only when the user asks for it, everything else is the same as in the package teleop_twist_keyboard.

Here's a screenshot of the xterm console:

<p align="center">
<img src="https://github.com/LucaPredieri/RT1Assignment3/blob/main/Schermata%202022-02-13%20alle%2000.40.06.png" width="485" height="356">
</p>

### Modality 3 node (final_assignment package)

__The modality 3 has the same aim of the modality 2, but it asks for an assisting stop when the robot is too close to a wall.__

To develop this modality I decided to reuse the second modality but modifing the most important part, the assignment of the key to the movement of the robot. To make the robot move the code uses the dictionary which is a code structure of python. Here we have:

```python
moveBindings = {
        'i':(1,0,0,0),
        'j':(0,0,0,1),
        'l':(0,0,0,-1),
        'k':(-1,0,0,0),
    }
```

Then we decide to get the inputs from the keyboard but everything is controlled by a new function, called ```python pop_dict()``` which permits to get rid of the commands that we shouldn't have when we're close to a wall. The function is the following: 

```python
def pop_it(dictionary):

    global ok_left
    global ok_right
    global ok_straight

    if not ok_straight and not ok_right and not ok_left:
        popped1 = dictionary.pop('i')
        popped2 = dictionary.pop('j')
        popped3 = dictionary.pop('l')
        print(bcolors.FAIL  + "Command 'i' disabled." + bcolors.ENDC, end="\r")
        print(bcolors.FAIL + "Command 'j' disabled." + bcolors.ENDC , end="\r")
        print(bcolors.FAIL + "Command 'l' disabled." + bcolors.ENDC , end="\r")
    elif not ok_left and not ok_straight and ok_right:
        popped1 = dictionary.pop('i')
        popped2 = dictionary.pop('j')
        print(bcolors.FAIL + "Command 'i' disabled." + bcolors.ENDC , end="\r")
        print(bcolors.FAIL + "Command 'j' disabled." + bcolors.ENDC , end="\r")
    elif ok_left and not ok_straight and not ok_right:
        popped1 = dictionary.pop('i')
        popped2 = dictionary.pop('l')
        print(bcolors.FAIL + "Command 'i' disabled." + bcolors.ENDC , end="\r")
        print(bcolors.FAIL + "Command 'l' disabled." + bcolors.ENDC , end="\r")
    elif not ok_left and ok_straight and not ok_right:
        popped1 = dictionary.pop('l')
        popped2 = dictionary.pop('j')
        print(bcolors.FAIL + "Command 'l' disabled." + bcolors.ENDC , end="\r")
        print(bcolors.FAIL + "Command 'j' disabled." + bcolors.ENDC , end="\r")
    elif ok_left and not ok_straight and ok_right:
        popped1 = dictionary.pop('i')
        print(bcolors.FAIL + "Command 'i' disabled." + bcolors.ENDC , end="\r")
    elif not ok_left and ok_straight and ok_right:
        popped1 = dictionary.pop('j')
        print(bcolors.FAIL + "Command 'j' disabled." + bcolors.ENDC , end="\r")
    elif ok_left and ok_straight and not ok_right:
        popped1 = dictionary.pop('l')
        print(bcolors.FAIL + "Command 'l' disabled." + bcolors.ENDC , end="\r")
```

As you can see, we're passing a dictionary to the function. The idea is that we will pass a copy of the original ```moveBindings``` dictionary, because we don't want the original informations to be lost when we're away from a wall! This is only the real difference from the other modality.

Here's a screenshot of the xterm console:

<p align="center">
<img src="https://github.com/LucaPredieri/RT1Assignment3/blob/main/Schermata%202022-02-13%20alle%2000.40.24.png" width="485" height="356">
</p>

## Conclusion and possible improvements

I'm really satisfied of the work, it was pretty tough especially by finding all the informations to create a good communication and developing each node. Thank's to the portability of ROS and the community I finalized the job. To conclude the communication of the nodes I will show yo with the node
```bash
rosrun rqt_graph rqt_graph
```

the relationship between all the nodes:

<p align="center">
<img src="https://github.com/LucaPredieri/RT1Assignment3/blob/main/Schermata%202022-02-13%20alle%2000.41.38.png">
</p>

__The possible improvements that can be done are:__
- We can manage better the User Interface, it is not so easy and it's full of various bugs.
- The modalities do only their jobs, but they can be completed with a lot of other fun things, like managing the speed and othe characteristics of the robot.
- As you can see, the input on the modality 3 is not really taken perfectly, it takes in the standard input the input keys and prints them. I tried to fix this problem but I couldn't fix it. Anyway I know for sure that if I will take some time over I can finally fix it.

(To implement the best code I could, I worked with my class mates, so I have to extend the credit to: Fabio Conti, Francesco Pagano, Alessandro Perri, Matteo Carlone)
