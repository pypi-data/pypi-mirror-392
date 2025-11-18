#!/usr/bin/env python3
"""
Basic Xbox Controller Usage Example

This example demonstrates basic usage of the XboxController class
including connection, reading controller state, and event handling.
"""

import time
import sys
sys.path.append('..')

from xbox_controller import XboxController

def main():
    """Main function demonstrating basic controller usage"""
    
    # Create controller instance
    controller = XboxController()
    
    try:
        # Connect to controller
        print("Connecting to Xbox controller...")
        controller.connect()
        
        # Get controller info
        info = controller.get_controller_info()
        print(f"Connected to: {info['name']}")
        print(f"Buttons: {info['button_count']}, Axes: {info['axis_count']}")
        print("-" * 50)
        
        print("Controller connected! Press Ctrl+C to exit.")
        print("Move joysticks and press buttons to see the output...")
        print()
        
        # Main loop
        while True:
            # Update controller state
            state = controller.update_state()
            
            if not state["connected"]:
                print("Controller disconnected!")
                break
            
            # Print controller state
            print(f"\rLeft Stick: [{state['left_joystick'][0]:6.3f}, {state['left_joystick'][1]:6.3f}] "
                  f"Right Stick: [{state['right_joystick'][0]:6.3f}, {state['right_joystick'][1]:6.3f}] "
                  f"Triggers: [{state['triggers'][0]:6.3f}, {state['triggers'][1]:6.3f}] "
                  f"Buttons: {state['pressed_buttons']}", end='', flush=True)
            
            time.sleep(0.1)  # Small delay to prevent high CPU usage
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Always disconnect when done
        controller.disconnect()
        print("Controller disconnected.")

if __name__ == "__main__":
    main()