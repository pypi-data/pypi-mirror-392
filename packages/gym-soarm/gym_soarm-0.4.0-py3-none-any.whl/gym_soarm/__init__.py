"""Gym SoArm environments.

A gymnasium environment for SO-ARM101 single-arm manipulation based on gym-aloha.
This package provides a simulation environment for the SO-ARM101 robotic arm with 
MuJoCo physics simulation, multi-camera support, and task-oriented reinforcement learning.

Features:
- SO-ARM101 6DOF robotic arm simulation
- Multi-camera system with runtime switching (overview, front, wrist cameras)
- Grid-based object placement with randomization
- OpenCV-based GUI viewer with keyboard controls
- Gymnasium/OpenAI Gym compatible interface
"""

from gymnasium.envs.registration import register

from gym_soarm.env import SoArmAlohaEnv
from gym_soarm.tasks.sim import SoArmTask, PickPlaceTask, StackingTask

__version__ = "0.4.0"
__author__ = "Masato Kawamura"
__email__ = "jp6uzv@gmail.com"

# Register the main environment
register(
    id="gym_soarm/PickAndPlaceCube-v0",
    entry_point="gym_soarm.env:SoArmAlohaEnv",
    max_episode_steps=200,
    kwargs={
        'task': 'pick_place',
        'obs_type': 'pixels_agent_pos',
        'render_mode': 'rgb_array',
        'reward_mode': 'math',
        'camera_config': 'diagonal_wrist'
    }
)

# Export main classes
__all__ = [
    'SoArmAlohaEnv',
    'SoArmTask',
    'PickPlaceTask', 
    'StackingTask',
]