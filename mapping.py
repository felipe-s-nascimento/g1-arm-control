import pygame
import sys

# Initialize pygame
pygame.init()

# Check if a controller is connected
if pygame.joystick.get_count() == 0:
    print("❌ No controller connected!")
    sys.exit(1)

# Get the first controller
joy = pygame.joystick.Joystick(0)
joy.init()

print(f"\n🎮 Controller: {joy.get_name()}")
print(f"📊 Total buttons: {joy.get_numbuttons()}")
print("\n👉 Press any button to see its number")
print("👉 Press L3 + R3 (buttons 10 and 11) together to exit\n")

print("-" * 50)

# Set to store buttons already shown
shown = set()

while True:
    pygame.event.pump()

    # Check each button
    for i in range(joy.get_numbuttons()):
        if joy.get_button(i):
            if i not in shown:
                print(f"✅ Button {i} pressed!")
                shown.add(i)
        else:
            if i in shown:
                shown.discard(i)

    # Exit if L3 and R3 are pressed together (buttons 10 and 11)
    if joy.get_button(10) and joy.get_button(11):
        print("\n👋 Exiting...")
        break

    pygame.time.wait(50)

pygame.quit()