import numpy as np
from scipy.spatial.transform import Rotation as R
from copy import deepcopy
import sys 
sys.path.append(".")
from robot import RobotInterface
import threading



class GravCompController: 

    def __init__(self, robot: RobotInterface):
        """
        Initialize Impedance Controller with pre-initialized resources.
        
        Args:
            robot: pylibfranka Robot instance
            model: pylibfranka Model for dynamics computation
        """
        self.robot = robot

        self.initialize() 
        self.state_lock = threading.Lock()
        print("here")
    
    def initialize(self): 

        # Get initial state
        initial_state = self.robot.state
        self.initial_ee = initial_state['ee']
        self.initial_qpos = deepcopy(initial_state['qpos'])
        self.initial_qvel = deepcopy(initial_state['qvel'])

    def step(self):
        
        robot_state = self.robot.state
        tau_d = np.zeros(7) * 0.0
        self.robot.step(tau_d)



if __name__ == "__main__":


    robot = RobotInterface("172.16.0.2") 
    
    controller = GravCompController(robot)
    while True: 
        controller.step()