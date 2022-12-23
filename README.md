# PA Robodog
Project Thesis Robodog at Zürich University of Applied Science

Important steps to follow:
1. Open a terminal and connect to the robot with ssh -X unitree@192.168.123.12. Enter the password 123. This is important as it adds the robot to the known hosts.
2. Start the robot
3. Start the UI (app.py) and connect to the robot
4. Press on sit and activate gesture recognition

Additional information:
The SDK files we created are in the example_files folder. Any additional SDK files must be scp'd to the robot's catkin_ws/utils/unitree_legged_sdk-3.2.0/examples folder.
The any new bash files like those in the bash_files folder belong in the home directory of the robot.
