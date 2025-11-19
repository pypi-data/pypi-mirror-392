import numpy as np
import threading
from scipy.spatial.transform import Rotation as R
from copy import deepcopy
from .robot import RobotInterface



class OSCController:

    def __init__(self, robot: RobotInterface):
        """
        Initialize OSC Controller with pre-initialized resources.
        
        Args:
            robot: pylibfranka Robot instance (or None for simulation)
        """

        self.robot = robot

        self.initialize()

        # Thread safety for shared state
        self.state_lock = threading.Lock()

    def initialize(self): 

        # Get initial state
        initial_state = self.robot.state
        self.initial_ee = initial_state['ee']
        self.initial_qpos = deepcopy(initial_state['qpos'])
        self.initial_qvel = deepcopy(initial_state['qvel'])

        self.ee_desired, self.kp, self.kd = self.initial_ee, np.ones(6) * 80, np.ones(6) * 4
        self.kp_null, self.kd_null = np.ones(7) * 1, np.ones(7) * 1

    def _update_desired(self, desired):
        """
        Update the desired end-effector pose, kp and kd
        This function is called by the server when a client sends new values
        Thread-safe update of shared state.
        
        Args:
            desired: Desired end-effector pose (4x4 matrix)
            kp: Cartesian stiffness gains (6-element array)
            kd: Cartesian damping gains (6-element array)
            kp_null: Null space stiffness gains (7-element array)
            kd_null: Null space damping gains (7-element array)
            pose_type: Type of pose command ('absolute', 'delta_from_init', 'delta_from_current')
        """
        with self.state_lock:
            self.ee_desired = desired


    def step(self): 

        # Read robot state
        state = self.robot.state
        jac = state['jac']
        ee = state['ee']
        q = state['qpos']
        dq = state['qvel']
        mm = state['mm']

        ee_goal = self.ee_desired

        position_error = ee_goal[:3, 3] - ee[:3, 3]

        rotation_error = R.from_matrix(ee_goal[:3, :3]) * R.from_matrix(ee[:3, :3]).inv()
        rotation_error_vec = rotation_error.as_rotvec()

        twist = np.zeros(6)
        twist[:3] = position_error
        twist[3:] = rotation_error_vec
        ee_vel = jac @ dq
        minv = np.linalg.inv(mm)
        mx_inv = jac @ minv @ jac.T

        if abs(np.linalg.det(mx_inv)) > 1e-2:
            mx = np.linalg.inv(mx_inv)
        else:
            mx = np.linalg.pinv(mx_inv)

        # operational space feedback torque
        feedback = jac.T @ mx @ (self.kp * twist - self.kd * ee_vel)

        # null space torque
        q0 = self.initial_qpos
        ddq = self.kp_null * (q0 - q) - self.kd_null * dq
        jbar = minv @ jac.T @ mx
        null = (np.eye(7) - jac.T @ jbar.T) @ ddq

        # Add coriolis compensation
        tau_d = feedback + null

        self.robot.step(tau_d)




if __name__ == "__main__":

    robot = RobotInterface()
    osc_controller = OSCController(robot)
    osc_controller.run()