#!/usr/bin/env python3
# main.py
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import sys
import pygame

from config.settings import BUTTON_START
from controller.g1_controller import G1LowLevelController

def main():
    if len(sys.argv) < 2:
        print("Usage: python g1_control_joystick.main <interface>")
        print("Example: python g1_control_joystick.main en1")
        sys.exit(1)

    interface = sys.argv[1]
    print("WARNING: Keep the robot suspended or in a safe area.")
    print("Make sure Sport Mode is DISABLED (via controller or app).")
    print("Use the Unitree controller (L2+R2) to enter developer mode, then use the DualSense to control the robot.")

    pygame.init()
    if pygame.joystick.get_count() == 0:
        print("No joystick found. Exiting...")
        sys.exit(1)

    joy = pygame.joystick.Joystick(0)
    print("Press Options (button 6) to start...")
    while True:
        pygame.event.pump()
        if joy.get_button(BUTTON_START):
            break

    controller = G1LowLevelController()
    controller.init(interface)
    controller.run()

if __name__ == "__main__":
    main()