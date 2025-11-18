#!/usr/bin/env python3
"""
Xbox Controller Command Line Interface

A simple CLI tool for testing Xbox controller connectivity and reading input.
"""

import argparse
import sys
import time
from .controller import XboxController
from .utils import get_pressed_button_names

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Xbox Controller CLI - Test and monitor Xbox controller input"
    )
    parser.add_argument(
        "--controller", "-c", 
        type=int, 
        default=0,
        help="Controller index to connect to (default: 0)"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["basic", "events", "info"],
        default="basic",
        help="Operation mode: basic (continuous), events (event-based), info (device info only)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=0,
        help="Duration to run in seconds (0 = run until interrupted)"
    )
    
    args = parser.parse_args()
    
    controller = XboxController()
    
    try:
        print(f"Connecting to controller {args.controller}...")
        controller.connect(args.controller)
        
        info = controller.get_controller_info()
        print(f"✅ Connected to: {info['name']}")
        print(f"   ID: {info['id']}")
        print(f"   Buttons: {info['button_count']}")
        print(f"   Axes: {info['axis_count']}")
        print("-" * 50)
        
        if args.mode == "info":
            return
        
        print(f"Mode: {args.mode}")
        print("Press Ctrl+C to exit")
        print("-" * 50)
        
        start_time = time.time()
        
        if args.mode == "basic":
            run_basic_mode(controller, args.duration, start_time)
        elif args.mode == "events":
            run_event_mode(controller, args.duration, start_time)
            
    except SystemExit as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    finally:
        controller.disconnect()
        print("🔌 Controller disconnected.")

def run_basic_mode(controller, duration, start_time):
    """Run in basic continuous monitoring mode"""
    print("🎮 Monitoring controller input...")
    
    while True:
        if duration > 0 and time.time() - start_time >= duration:
            break
            
        state = controller.update_state()
        
        if not state["connected"]:
            print("❌ Controller disconnected!")
            break
        
        # Create status line
        left_stick = f"[{state['left_joystick'][0]:6.3f}, {state['left_joystick'][1]:6.3f}]"
        right_stick = f"[{state['right_joystick'][0]:6.3f}, {state['right_joystick'][1]:6.3f}]"
        triggers = f"[{state['triggers'][0]:6.3f}, {state['triggers'][1]:6.3f}]"
        
        button_names = get_pressed_button_names({i: i in state['pressed_buttons'] for i in range(16)})
        buttons_str = ", ".join(button_names) if button_names else "None"
        
        print(f"\rLeft: {left_stick} | Right: {right_stick} | Triggers: {triggers} | Buttons: {buttons_str}", 
              end='', flush=True)
        
        time.sleep(0.1)

def run_event_mode(controller, duration, start_time):
    """Run in event-based monitoring mode"""
    print("🎯 Event-based monitoring...")
    
    previous_state = controller.update_state()
    
    while True:
        if duration > 0 and time.time() - start_time >= duration:
            break
            
        current_state = controller.update_state()
        
        if not current_state["connected"]:
            print("❌ Controller disconnected!")
            break
        
        # Check for button events
        if len(current_state["pressed_buttons"]) != len(previous_state["pressed_buttons"]):
            new_buttons = set(current_state["pressed_buttons"]) - set(previous_state["pressed_buttons"])
            released_buttons = set(previous_state["pressed_buttons"]) - set(current_state["pressed_buttons"])
            
            if new_buttons:
                button_names = get_pressed_button_names({i: i in new_buttons for i in range(16)})
                print(f"🔘 PRESSED: {', '.join(button_names)}")
            
            if released_buttons:
                button_names = get_pressed_button_names({i: i in released_buttons for i in range(16)})
                print(f"🔘 RELEASED: {', '.join(button_names)}")
        
        # Check for significant joystick movement
        left_threshold = 0.3
        right_threshold = 0.3
        
        # Left joystick movement
        if (abs(current_state["left_joystick"][0]) > left_threshold or 
            abs(current_state["left_joystick"][1]) > left_threshold):
            if (abs(previous_state["left_joystick"][0]) <= left_threshold and 
                abs(previous_state["left_joystick"][1]) <= left_threshold):
                print(f"🕹️  LEFT JOYSTICK: {current_state['left_joystick']}")
        
        # Right joystick movement
        if (abs(current_state["right_joystick"][0]) > right_threshold or 
            abs(current_state["right_joystick"][1]) > right_threshold):
            if (abs(previous_state["right_joystick"][0]) <= right_threshold and 
                abs(previous_state["right_joystick"][1]) <= right_threshold):
                print(f"🕹️  RIGHT JOYSTICK: {current_state['right_joystick']}")
        
        # Trigger events
        trigger_threshold = 0.5
        if (current_state["triggers"][0] > trigger_threshold and 
            previous_state["triggers"][0] <= trigger_threshold):
            print(f"🔫 LEFT TRIGGER: {current_state['triggers'][0]:.3f}")
        
        if (current_state["triggers"][1] > trigger_threshold and 
            previous_state["triggers"][1] <= trigger_threshold):
            print(f"🔫 RIGHT TRIGGER: {current_state['triggers'][1]:.3f}")
        
        previous_state = current_state
        time.sleep(0.05)

if __name__ == "__main__":
    main()