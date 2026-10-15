# config.py
import numpy as np

# =========================================================
# GENERAL PARAMETERS
# =========================================================
DT = 0.002              # 500 Hz
NUM_MOTORS = 29

# Global gains (fallback if the joint is not in JOINT_GAINS)
KP = 40.0
KD = 1.0

# Safety timings
INTERPOLATION_DURATION = 3.0   # seconds to go from current pose to INITIAL_TARGETS
PLAYBACK_DURATION      = 2.5   # seconds per pose during playback
MAX_DELTA_PER_CYCLE    = 0.015 # rad/cycle (joystick rate limit)

# =========================================================
# JOYSTICK BUTTONS (DualSense on macOS)
# =========================================================
BUTTON_RECORD = 7    # L3
BUTTON_PLAY   = 8    # R3
BUTTON_CLEAR  = 4    # Share
BUTTON_MODE   = 15   # Touchpad
BUTTON_START  = 6    # Options

# =========================================================
# JOINT INDICES
# =========================================================
JOINT_NAMES = {
    # Left Leg
    "LEFT_HIP_PITCH": 0,
    "LEFT_HIP_ROLL": 1,
    "LEFT_HIP_YAW": 2,
    "LEFT_KNEE": 3,
    "LEFT_ANKLE_PITCH": 4,
    "LEFT_ANKLE_ROLL": 5,
    # Right Leg
    "RIGHT_HIP_PITCH": 6,
    "RIGHT_HIP_ROLL": 7,
    "RIGHT_HIP_YAW": 8,
    "RIGHT_KNEE": 9,
    "RIGHT_ANKLE_PITCH": 10,
    "RIGHT_ANKLE_ROLL": 11,
    # Waist
    "WAIST_YAW": 12,
    "WAIST_ROLL": 13,
    "WAIST_PITCH": 14,
    # Left Arm
    "LEFT_SHOULDER_PITCH": 15,
    "LEFT_SHOULDER_ROLL": 16,
    "LEFT_SHOULDER_YAW": 17,
    "LEFT_ELBOW": 18,
    "LEFT_WRIST_ROLL": 19,
    "LEFT_WRIST_PITCH": 20,
    "LEFT_WRIST_YAW": 21,
    # Right Arm
    "RIGHT_SHOULDER_PITCH": 22,
    "RIGHT_SHOULDER_ROLL": 23,
    "RIGHT_SHOULDER_YAW": 24,
    "RIGHT_ELBOW": 25,
    "RIGHT_WRIST_ROLL": 26,
    "RIGHT_WRIST_PITCH": 27,
    "RIGHT_WRIST_YAW": 28,
}

# =========================================================
# JOINT LIMITS (rad)
# =========================================================
JOINT_LIMITS = {
    # Legs
    "LEFT_HIP_PITCH": (-2.5307, 2.8798),
    "LEFT_HIP_ROLL": (-0.5236, 2.9671),
    "LEFT_HIP_YAW": (-2.7576, 2.7576),
    "LEFT_KNEE": (-0.087267, 2.8798),
    "LEFT_ANKLE_PITCH": (-0.87267, 0.5236),
    "LEFT_ANKLE_ROLL": (-0.2618, 0.2618),
    "RIGHT_HIP_PITCH": (-2.5307, 2.8798),
    "RIGHT_HIP_ROLL": (-2.9671, 0.5236),
    "RIGHT_HIP_YAW": (-2.7576, 2.7576),
    "RIGHT_KNEE": (-0.087267, 2.8798),
    "RIGHT_ANKLE_PITCH": (-0.87267, 0.5236),
    "RIGHT_ANKLE_ROLL": (-0.2618, 0.2618),
    # Waist
    "WAIST_YAW": (-2.618, 2.618),
    "WAIST_ROLL": (-0.52, 0.52),
    "WAIST_PITCH": (-0.52, 0.52),
    # Left Arm
    "LEFT_SHOULDER_PITCH": (-3.0892, 2.6704),
    "LEFT_SHOULDER_ROLL": (-1.5882, 2.2515),
    "LEFT_SHOULDER_YAW": (-2.618, 2.618),
    "LEFT_ELBOW": (-1.0472, 2.0944),
    "LEFT_WRIST_ROLL": (-1.972222054, 1.972222054),
    "LEFT_WRIST_PITCH": (-1.614429558, 1.614429558),
    "LEFT_WRIST_YAW": (-1.614429558, 1.614429558),
    # Right Arm
    "RIGHT_SHOULDER_PITCH": (-3.0892, 2.6704),
    "RIGHT_SHOULDER_ROLL": (-2.2515, 1.5882),
    "RIGHT_SHOULDER_YAW": (-2.618, 2.618),
    "RIGHT_ELBOW": (-1.0472, 2.0944),
    "RIGHT_WRIST_ROLL": (-1.972222054, 1.972222054),
    "RIGHT_WRIST_PITCH": (-1.614429558, 1.614429558),
    "RIGHT_WRIST_YAW": (-1.614429558, 1.614429558),
}

# =========================================================
# PER-JOINT GAINS (kp, kd) — calibrated for real hardware
# =========================================================
# Legs and waist are stiff; arms and wrists are soft.
# If you hear buzzing/shaking, reduce kp by 20% and test again.
JOINT_GAINS = {
    # Legs
    "LEFT_HIP_PITCH":   (100.0, 2.0),
    "LEFT_HIP_ROLL":    (100.0, 2.0),
    "LEFT_HIP_YAW":     (100.0, 2.0),
    "LEFT_KNEE":        (150.0, 2.0),
    "LEFT_ANKLE_PITCH": (40.0, 2.0),
    "LEFT_ANKLE_ROLL":  (40.0, 2.0),
    "RIGHT_HIP_PITCH":  (100.0, 2.0),
    "RIGHT_HIP_ROLL":   (100.0, 2.0),
    "RIGHT_HIP_YAW":    (100.0, 2.0),
    "RIGHT_KNEE":       (150.0, 2.0),
    "RIGHT_ANKLE_PITCH": (40.0, 2.0),
    "RIGHT_ANKLE_ROLL":  (40.0, 2.0),
    # Waist
    "WAIST_YAW":   (100.0, 2.0),
    "WAIST_ROLL":  (100.0, 2.0),
    "WAIST_PITCH": (100.0, 2.0),
    # Left Arm
    "LEFT_SHOULDER_PITCH": (40.0, 1.0),
    "LEFT_SHOULDER_ROLL":  (40.0, 1.0),
    "LEFT_SHOULDER_YAW":   (40.0, 1.0),
    "LEFT_ELBOW":          (40.0, 1.0),
    "LEFT_WRIST_ROLL":     (20.0, 0.5),
    "LEFT_WRIST_PITCH":    (20.0, 0.5),
    "LEFT_WRIST_YAW":      (20.0, 0.5),
    # Right Arm
    "RIGHT_SHOULDER_PITCH": (40.0, 1.0),
    "RIGHT_SHOULDER_ROLL":  (40.0, 1.0),
    "RIGHT_SHOULDER_YAW":   (40.0, 1.0),
    "RIGHT_ELBOW":          (40.0, 1.0),
    "RIGHT_WRIST_ROLL":     (20.0, 0.5),
    "RIGHT_WRIST_PITCH":    (20.0, 0.5),
    "RIGHT_WRIST_YAW":      (20.0, 0.5),
}

# =========================================================
# CONTROL MODES
# =========================================================
MODES = [
    {  # mode 0: right arm
        "name": "RIGHT",
        "joints": {
            "yaw": "RIGHT_SHOULDER_YAW",
            "roll": "RIGHT_SHOULDER_ROLL",
            "pitch": "RIGHT_SHOULDER_PITCH",
            "elbow": "RIGHT_ELBOW",
            "wrist_roll": "RIGHT_WRIST_ROLL",
            "wrist_pitch": "RIGHT_WRIST_PITCH",
            "wrist_yaw": "RIGHT_WRIST_YAW",
        }
    },
    {  # mode 1: left arm
        "name": "LEFT",
        "joints": {
            "yaw": "LEFT_SHOULDER_YAW",
            "roll": "LEFT_SHOULDER_ROLL",
            "pitch": "LEFT_SHOULDER_PITCH",
            "elbow": "LEFT_ELBOW",
            "wrist_roll": "LEFT_WRIST_ROLL",
            "wrist_pitch": "LEFT_WRIST_PITCH",
            "wrist_yaw": "LEFT_WRIST_YAW",
        }
    }
]

# =========================================================
# INITIAL POSE (real standing pose, NOT zero!)
# =========================================================
INITIAL_TARGETS = {
    # Left Leg
    "LEFT_HIP_PITCH":  -0.1,
    "LEFT_HIP_ROLL":    0.0,
    "LEFT_HIP_YAW":     0.0,
    "LEFT_KNEE":        0.3,
    "LEFT_ANKLE_PITCH": -0.2,
    "LEFT_ANKLE_ROLL":  0.0,
    # Right Leg
    "RIGHT_HIP_PITCH":  -0.1,
    "RIGHT_HIP_ROLL":    0.0,
    "RIGHT_HIP_YAW":     0.0,
    "RIGHT_KNEE":        0.3,
    "RIGHT_ANKLE_PITCH": -0.2,
    "RIGHT_ANKLE_ROLL":  0.0,
    # Waist
    "WAIST_YAW":   0.0,
    "WAIST_ROLL":  0.0,
    "WAIST_PITCH": 0.0,
    # Left Arm (relaxed)
    "LEFT_SHOULDER_PITCH": 0.0,
    "LEFT_SHOULDER_ROLL":  0.0,
    "LEFT_SHOULDER_YAW":   0.0,
    "LEFT_ELBOW":          0.3,
    "LEFT_WRIST_ROLL":     0.0,
    "LEFT_WRIST_PITCH":    0.0,
    "LEFT_WRIST_YAW":      0.0,
    # Right Arm (relaxed)
    "RIGHT_SHOULDER_PITCH": 0.0,
    "RIGHT_SHOULDER_ROLL":  0.0,
    "RIGHT_SHOULDER_YAW":   0.0,
    "RIGHT_ELBOW":          0.3,
    "RIGHT_WRIST_ROLL":     0.0,
    "RIGHT_WRIST_PITCH":    0.0,
    "RIGHT_WRIST_YAW":      0.0,
}