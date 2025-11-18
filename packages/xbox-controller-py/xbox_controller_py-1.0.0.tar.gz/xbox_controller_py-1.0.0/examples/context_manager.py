#!/usr/bin/env python3
"""
Xbox Controller Context Manager Example

This example demonstrates using the XboxController class as a context manager
for automatic resource management.
"""

import time
import sys
sys.path.append('..')

from xbox_controller import XboxController

def main():
    """Main function demonstrating context manager usage"""
    
    try:
        # Use controller as context manager for automatic cleanup
        with XboxController() as controller:
            print("Controller connected using context manager!")
            
            # Get controller info
            info = controller.get_controller_info()
            print(f"Device: {info['name']}")
            print("-" * 40)
            
            print("Press buttons and move joysticks...")
            print("Press Ctrl+C to exit\n")
            
            # Monitor controller for 10 seconds
            start_time = time.time()
            while time.time() - start_time < 10:
                # Update and get state
                state = controller.update_state()
                
                # Only print if there are button presses or significant joystick movement
                if (state["pressed_buttons"] or 
                    abs(state["left_joystick"][0]) > 0.1 or 
                    abs(state["left_joystick"][1]) > 0.1 or
                    abs(state["right_joystick"][0]) > 0.1 or
                    abs(state["right_joystick"][1]) > 0.1 or
                    abs(state["triggers"][0]) > 0.1 or
                    abs(state["triggers"][1]) > 0.1):
                    
                    print(f"Left: {state['left_joystick']} | "
                          f"Right: {state['right_joystick']} | "
                          f"Triggers: {state['triggers']} | "
                          f"Buttons: {state['pressed_buttons']}")
                
                time.sleep(0.1)
            
            print("\nTime's up! Controller will be automatically disconnected.")
            
    except SystemExit as e:
        print(f"Connection error: {e}")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        
    # Controller is automatically disconnected when exiting the context
    print("Controller disconnected automatically.")

if __name__ == "__main__":
    main()