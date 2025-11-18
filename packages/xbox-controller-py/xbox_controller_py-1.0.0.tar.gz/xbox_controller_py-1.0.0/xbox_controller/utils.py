"""
Utility functions for Xbox controller handling
"""

def format_axis_value(value):
    """
    Format axis value to 3 decimal places
    
    Args:
        value (float): Axis value to format
        
    Returns:
        str: Formatted axis value string
    """
    return f"{value:7.3f}"


def get_controller_state(joystick, buttons, axes):
    """
    Get controller state from raw joystick data
    
    Args:
        joystick: Pygame joystick object
        buttons (dict): Dictionary of button states {button_id: state}
        axes (dict): Dictionary of axis values {axis_id: value}
        
    Returns:
        tuple: (left_joystick, right_joystick, triggers, pressed_buttons)
            - left_joystick: [x, y] values for left joystick
            - right_joystick: [x, y] values for right joystick  
            - triggers: [left_trigger, right_trigger] values
            - pressed_buttons: List of pressed button IDs
    """
    # Get joystick states
    left_joystick = [axes.get(0, 0), axes.get(1, 0)]  # Left joystick X, Y
    right_joystick = [axes.get(2, 0), axes.get(3, 0)]  # Right joystick X, Y
    triggers = [axes.get(4, 0), axes.get(5, 0)]  # Left trigger, Right trigger
    
    # Get pressed buttons
    pressed_buttons = []
    for button_id, state in buttons.items():
        if state:
            pressed_buttons.append(button_id)
    
    return left_joystick, right_joystick, triggers, pressed_buttons


def get_button_name(button_id):
    """
    Get button name from button ID
    
    Args:
        button_id (int): Button ID number
        
    Returns:
        str: Button name or "Button {id}" if not found
    """
    button_names = {
        0: "A", 1: "B", 2: "X", 3: "Y",
        4: "LB", 5: "RB", 6: "Back", 7: "Start",
        8: "Left Stick", 9: "Right Stick", 
        10: "LT", 11: "RT",
        12: "D-pad Up", 13: "D-pad Down", 14: "D-pad Left", 15: "D-pad Right"
    }
    
    return button_names.get(button_id, f"Button {button_id}")


def get_pressed_button_names(buttons):
    """
    Get list of pressed button names
    
    Args:
        buttons (dict): Dictionary of button states {button_id: state}
        
    Returns:
        list: List of pressed button names
    """
    pressed_names = []
    for button_id, state in buttons.items():
        if state:
            pressed_names.append(get_button_name(button_id))
    
    return pressed_names