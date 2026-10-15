# controller.py
import time
import pygame
from unitree_sdk2py.core.channel import (
    ChannelPublisher, ChannelSubscriber, ChannelFactoryInitialize
)
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
from unitree_sdk2py.utils.crc import CRC

from config.settings import (
    DT, NUM_MOTORS, KP, KD, JOINT_NAMES, JOINT_LIMITS, MODES, INITIAL_TARGETS,
    BUTTON_RECORD, BUTTON_PLAY, BUTTON_CLEAR, BUTTON_MODE, BUTTON_START,
    INTERPOLATION_DURATION, PLAYBACK_DURATION, MAX_DELTA_PER_CYCLE, JOINT_GAINS
)


def get_gains(joint_name):
    """Returns (kp, kd) per joint, with a global fallback."""
    if joint_name in JOINT_GAINS:
        return JOINT_GAINS[joint_name]
    return (KP, KD)


class G1LowLevelController:
    def __init__(self):
        self.running_time = 0.0
        self.crc = CRC()
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        self.low_state = None
        self.mode_machine = 0
        self.has_mode = False
        self.pub = None
        self.sub = None

        # Smoothing
        self.target_angles = {}
        self.smoothing = 0.8
        self.rate_gain = 0.5

        # Mode
        self.modes = MODES
        self.current_mode = 0

        # Recording / playback
        self.recorded_poses = []
        self.is_playing = False
        self.loop_playback = False
        self.playback_index = 0
        self.playback_start_time = 0.0
        self.playback_duration = PLAYBACK_DURATION
        self.playback_start_pose = {}

        # Joystick
        self.joy = None

    # =========================================================
    # INITIALIZATION
    # =========================================================
    def init(self, network_interface: str):
        ChannelFactoryInitialize(0, network_interface)

        self.pub = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.pub.Init()
        self.sub = ChannelSubscriber("rt/lowstate", LowState_)
        self.sub.Init(self.low_state_handler)

        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
            print(f"Joystick detected: {self.joy.get_name()}")
        else:
            print("No joystick found.")
            self.joy = None

        print("Waiting for robot state...")
        while not self.has_mode:
            time.sleep(0.01)
        self.init_low_cmd()

    def low_state_handler(self, msg: LowState_):
        self.low_state = msg
        if not self.has_mode:
            self.mode_machine = msg.mode_machine
            self.has_mode = True

    # =========================================================
    # UTILITIES
    # =========================================================
    def clamp_angle(self, joint_name, angle):
        if joint_name not in JOINT_LIMITS:
            return angle
        min_ang, max_ang = JOINT_LIMITS[joint_name]
        return max(min_ang, min(angle, max_ang))

    def write_cmd(self, idx, q, kp, kd, tau=0.0):
        self.low_cmd.motor_cmd[idx].mode = 1
        self.low_cmd.motor_cmd[idx].q = q
        self.low_cmd.motor_cmd[idx].dq = 0.0
        self.low_cmd.motor_cmd[idx].kp = kp
        self.low_cmd.motor_cmd[idx].kd = kd
        self.low_cmd.motor_cmd[idx].tau = tau

    def publish(self):
        self.low_cmd.mode_machine = self.mode_machine
        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.pub.Write(self.low_cmd)

    # =========================================================
    # SMOOTH INITIALIZATION (Damping -> Interpolation with ramp)
    # =========================================================
    def init_low_cmd(self):
        freq = 500
        step = 1.0 / freq

        # -------- PHASE 0: Pure damping --------
        print("[Init] Phase 0: Pure damping (1.5s)...")
        for _ in range(int(1.5 * freq)):
            for name, idx in JOINT_NAMES.items():
                self.write_cmd(idx, 0.0, kp=0.0, kd=0.5, tau=0.0)
            self.publish()
            time.sleep(step)

        # -------- PHASE 1: Interpolation with gain ramp --------
        print(f"[Init] Phase 1: Interpolating ({INTERPOLATION_DURATION}s)...")
        joints_info = []
        for name, angle in INITIAL_TARGETS.items():
            idx = JOINT_NAMES[name]
            current_pos = self.low_state.motor_state[idx].q
            joints_info.append((idx, name, current_pos, angle))

        num_steps = int(INTERPOLATION_DURATION * freq)
        for step_i in range(num_steps + 1):
            t = step_i / num_steps
            t_smooth = t * t * (3.0 - 2.0 * t)  # smoothstep
            for idx, name, start_pos, target_pos in joints_info:
                q_interp = (1 - t_smooth) * start_pos + t_smooth * target_pos
                q_interp = self.clamp_angle(name, q_interp)
                kp_max, kd_max = get_gains(name)
                # Ramp: kp starts at 0, kd starts at 0.5
                kp_interp = t_smooth * kp_max
                kd_interp = 0.5 + t_smooth * (kd_max - 0.5)
                self.write_cmd(idx, q_interp, kp=kp_interp, kd=kd_interp)
            self.publish()
            if step_i < num_steps:
                time.sleep(step)

        # -------- PHASE 2: Confirm final position --------
        for idx, name, _, target_pos in joints_info:
            q_final = self.clamp_angle(name, target_pos)
            kp, kd = get_gains(name)
            self.write_cmd(idx, q_final, kp=kp, kd=kd)
        self.publish()

        for name in INITIAL_TARGETS:
            self.target_angles[name] = INITIAL_TARGETS[name]

        print("[Init] Ready. Robot under low-level control.")

    # =========================================================
    # JOYSTICK
    # =========================================================
    def _apply_delta(self, joint_name, delta):
        """Applies delta with per-cycle rate limiting."""
        delta = max(-MAX_DELTA_PER_CYCLE, min(delta, MAX_DELTA_PER_CYCLE))
        self.target_angles[joint_name] += delta
        self.target_angles[joint_name] = self.clamp_angle(
            joint_name, self.target_angles[joint_name]
        )

    def read_joystick_incremental(self):
        if self.joy is None:
            return
        pygame.event.pump()

        joints = self.modes[self.current_mode]["joints"]
        controlled_joints = list(joints.values())

        for name in controlled_joints:
            if name not in self.target_angles:
                idx = JOINT_NAMES[name]
                self.target_angles[name] = self.low_state.motor_state[idx].q

        left_stick_x = self.joy.get_axis(0)
        left_stick_y = self.joy.get_axis(1)
        right_stick_x = self.joy.get_axis(2)
        right_stick_y = self.joy.get_axis(3)
        l2_trigger = self.joy.get_axis(4)
        r2_trigger = self.joy.get_axis(5)

        deadzone = 0.05
        left_stick_x = 0 if abs(left_stick_x) < deadzone else left_stick_x
        left_stick_y = 0 if abs(left_stick_y) < deadzone else left_stick_y
        right_stick_x = 0 if abs(right_stick_x) < deadzone else right_stick_x
        right_stick_y = 0 if abs(right_stick_y) < deadzone else right_stick_y
        r2_trigger = 0 if r2_trigger < deadzone else r2_trigger
        l2_trigger = 0 if l2_trigger < deadzone else l2_trigger

        # Buttons for wrist_yaw
        if self.joy.get_button(9):
            self._apply_delta(joints["wrist_yaw"], self.smoothing * DT)
        if self.joy.get_button(10):
            self._apply_delta(joints["wrist_yaw"], -self.smoothing * DT)

        # Buttons for wrist_pitch
        if self.joy.get_button(13):
            self._apply_delta(joints["wrist_pitch"], self.smoothing * DT)
        if self.joy.get_button(14):
            self._apply_delta(joints["wrist_pitch"], -self.smoothing * DT)

        vel_yaw   = left_stick_x * self.rate_gain
        vel_elbow = left_stick_y * self.rate_gain
        vel_roll  = right_stick_x * self.rate_gain
        vel_pitch = right_stick_y * self.rate_gain
        vel_wrist = (r2_trigger - l2_trigger) * self.rate_gain

        self._apply_delta(joints["yaw"],         vel_yaw * DT)
        self._apply_delta(joints["roll"],        vel_roll * DT)
        self._apply_delta(joints["pitch"],       vel_pitch * DT)
        self._apply_delta(joints["elbow"],       vel_elbow * DT)
        self._apply_delta(joints["wrist_roll"],  vel_wrist * DT)

    # =========================================================
    # RECORDING / PLAYBACK
    # =========================================================
    def record_current_pose(self):
        pose = {name: angle for name, angle in self.target_angles.items()}
        self.recorded_poses.append(pose)
        print(f"[Recorded] Pose {len(self.recorded_poses)}")

    def start_playback(self, loop=False):
        if not self.recorded_poses:
            print("No poses recorded.")
            return
        if self.is_playing:
            print("Already playing.")
            return
        self.loop_playback = loop
        self.is_playing = True
        self.playback_index = 0
        self.playback_start_time = self.running_time
        self.playback_start_pose = dict(self.target_angles)
        mode = "LOOP" if loop else "single"
        print(f"Starting {mode} playback of {len(self.recorded_poses)} pose(s)...")

    def update_playback(self):
        if not self.is_playing:
            return

        if self.playback_index >= len(self.recorded_poses):
            if self.loop_playback:
                # Go back to the start, starting from the last recorded pose
                self.playback_start_pose = dict(self.recorded_poses[-1])
                self.playback_index = 0
                self.playback_start_time = self.running_time
            else:
                self.is_playing = False
                print("Playback finished.")
                return

        elapsed = self.running_time - self.playback_start_time
        if elapsed >= self.playback_duration:
            self.playback_index += 1
            if self.playback_index < len(self.recorded_poses):
                self.playback_start_time = self.running_time
            return

        t = elapsed / self.playback_duration
        t = t * t * (3.0 - 2.0 * t)  # smoothstep

        if self.playback_index == 0:
            target_pose = self.recorded_poses[0]
            for name in target_pose:
                start = self.playback_start_pose.get(name, target_pose[name])
                self.target_angles[name] = (1 - t) * start + t * target_pose[name]
        else:
            prev_pose = self.recorded_poses[self.playback_index - 1]
            next_pose = self.recorded_poses[self.playback_index]
            for name in next_pose:
                start = prev_pose.get(name, next_pose[name])
                self.target_angles[name] = (1 - t) * start + t * next_pose[name]

    def clear_poses(self):
        self.recorded_poses.clear()
        self.is_playing = False
        self.loop_playback = False
        print("All poses have been cleared.")

    # =========================================================
    # APPLYING TARGETS
    # =========================================================
    def apply_target_angles(self):
        for name, angle in self.target_angles.items():
            idx = JOINT_NAMES[name]
            clamped_angle = self.clamp_angle(name, angle)
            kp, kd = get_gains(name)
            self.write_cmd(idx, clamped_angle, kp=kp, kd=kd)

    # =========================================================
    # MAIN LOOP
    # =========================================================
    def update_command(self):
        if self.low_state is None:
            return
        self.running_time += DT

        if self.joy is not None:
            pygame.event.pump()

            # L3 = record current pose
            if self.joy.get_button(BUTTON_RECORD):
                self.record_current_pose()
                while self.joy.get_button(BUTTON_RECORD):
                    pygame.event.pump()
                    time.sleep(0.05)

            # R3 = play once
            if self.joy.get_button(BUTTON_PLAY):
                if not self.is_playing:
                    self.start_playback(loop=False)
                while self.joy.get_button(BUTTON_PLAY):
                    pygame.event.pump()
                    time.sleep(0.05)

            # Options = play in LOOP (press again to stop)
            if self.joy.get_button(BUTTON_START):
                if self.is_playing:
                    self.is_playing = False
                    self.loop_playback = False
                    print("Loop playback STOPPED.")
                else:
                    if not self.recorded_poses:
                        print("No poses recorded. Record with L3 first.")
                    else:
                        self.start_playback(loop=True)
                        print("LOOP playback started. Press Options again to stop.")
                while self.joy.get_button(BUTTON_START):
                    pygame.event.pump()
                    time.sleep(0.05)

            # Share = clear all poses
            if self.joy.get_button(BUTTON_CLEAR):
                self.clear_poses()
                while self.joy.get_button(BUTTON_CLEAR):
                    pygame.event.pump()
                    time.sleep(0.05)

            # Touchpad = switch arm
            if self.joy.get_button(BUTTON_MODE):
                self.current_mode = 1 - self.current_mode
                print(f"Mode: arm {self.modes[self.current_mode]['name']}")
                while self.joy.get_button(BUTTON_MODE):
                    pygame.event.pump()
                    time.sleep(0.05)

        if self.is_playing:
            self.update_playback()
        else:
            self.read_joystick_incremental()

        self.apply_target_angles()
        self.publish()

    def run(self):
        print("Control loop started... Ctrl+C to stop.")
        try:
            while True:
                start = time.perf_counter()
                self.update_command()
                elapsed = time.perf_counter() - start
                if elapsed < DT:
                    time.sleep(DT - elapsed)
        except KeyboardInterrupt:
            print("\nInterrupted. Applying damping...")
            self._safe_shutdown()

    def _safe_shutdown(self):
        if self.low_state is None:
            return
        for _ in range(500):
            for name, idx in JOINT_NAMES.items():
                self.write_cmd(idx, 0.0, kp=0.0, kd=0.5, tau=0.0)
            self.publish()
            time.sleep(1.0 / 500.0)
        print("Damping applied. Shutting down.")


# =========================================================
# ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    import sys
    interface = sys.argv[1] if len(sys.argv) > 1 else "lo0"
    ctrl = G1LowLevelController()
    ctrl.init(interface)
    ctrl.run()