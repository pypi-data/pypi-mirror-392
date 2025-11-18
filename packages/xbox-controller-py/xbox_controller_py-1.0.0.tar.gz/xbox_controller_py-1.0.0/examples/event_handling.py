#!/usr/bin/env python3
"""
Xbox Controller Event Handling Example

This example demonstrates advanced event handling with the XboxController class,
including button press detection and state change monitoring.
"""

import time
import sys
sys.path.append('..')

from xbox_controller import XboxController
from xbox_controller.utils import get_pressed_button_names

def main():
    """Main function demonstrating event handling"""
    
    controller = XboxController()
    
    try:
        print("Connecting to Xbox controller...")
        controller.connect()
        
        info = controller.get_controller_info()
        print(f"Connected to: {info['name']}")
        print("-" * 50)
        
        print("Event-based controller monitoring")
        print("Press buttons to see individual events...")
        print("Press Ctrl+C to exit\n")
        
        previous_state = controller.update_state()
        
        while True:
            # Update state
            current_state = controller.update_state()
            
            if not current_state["connected"]:
                print("Controller disconnected!")
                break
            
            # Check for button press events
            if len(current_state["pressed_buttons"]) != len(previous_state["pressed_buttons"]):
                new_buttons = set(current_state["pressed_buttons"]) - set(previous_state["pressed_buttons"])
                released_buttons = set(previous_state["pressed_buttons"]) - set(current_state["pressed_buttons"])
                
                if new_buttons:
                    button_names = [f"Button {btn}" for btn in new_buttons]
                    print(f"🎮 BUTTONS PRESSED: {', '.join(button_names)}")
                
                if released_buttons:
                    button_names = [f"Button {btn}" for btn in released_buttons]
                    print(f"🎮 BUTTONS RELEASED: {', '.join(button_names)}")
            
            # Check for significant joystick movement
            left_threshold = 0.3
            right_threshold = 0.3
            
            # Left joystick movement detection
            if (abs(current_state["left_joystick"][0]) > left_threshold or 
                abs(current_state["left_joystick"][1]) > left_threshold):
                if (abs(previous_state["left_joystick"][0]) <= left_threshold and 
                    abs(previous_state["left_joystick"][1]) <= left_threshold):
                    print(f"🕹️  LEFT JOYSTICK MOVED: {current_state['left_joystick']}")
            
            # Right joystick movement detection  
            if (abs(current_state["right_joystick"][0]) > right_threshold or 
                abs(current_state["right_joystick"][1]) > right_threshold):
                if (abs(previous_state["right_joystick"][0]) <= right_threshold and 
                    abs(previous_state["right_joystick"][1]) <= right_threshold):
                    print(f"🕹️  RIGHT JOYSTICK MOVED: {current_state['right_joystick']}")
            
            # Trigger press detection
            trigger_threshold = 0.5
            if (current_state["triggers"][0] > trigger_threshold and 
                previous_state["triggers"][0] <= trigger_threshold):
                print(f"🔫 LEFT TRIGGER PRESSED: {current_state['triggers'][0]:.3f}")
            
            if (current_state["triggers"][1] > trigger_threshold and 
                previous_state["triggers"][1] <= trigger_threshold):
                print(f"🔫 RIGHT TRIGGER PRESSED: {current_state['triggers'][1]:.3f}")
            
            # Update previous state
            previous_state = current_state
            
            time.sleep(0.05)  # Faster update for better event detection
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        controller.disconnect()
        print("Controller disconnected.")

if __name__ == "__main__":
    main()