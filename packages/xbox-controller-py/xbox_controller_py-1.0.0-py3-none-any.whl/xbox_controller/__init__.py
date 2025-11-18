"""
Xbox Controller Python Package

A Python package for reading and handling Xbox controller input using pygame.

This package provides simple and intuitive functions to:
- Initialize Xbox controller connection
- Read controller state (buttons, joysticks, triggers)
- Handle controller events

Author: Xbox Controller Py
Version: 1.0.0
"""

from .controller import XboxController
from .utils import format_axis_value, get_controller_state, get_button_name, get_pressed_button_names

__version__ = "1.0.0"
__author__ = "Xbox Controller Py"
__all__ = ["XboxController", "format_axis_value", "get_controller_state", "get_button_name", "get_pressed_button_names"]