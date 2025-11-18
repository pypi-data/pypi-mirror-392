# XboxControllerPy

[\[ 中文文档 \]](README_zh.md)

A Python package for reading and handling Xbox controller input using pygame.

## Features

- 🎮 Easy Xbox controller connection and management
- 🕹️ Real-time joystick and button state reading
- 🔫 Trigger button support
- 🎯 Event-based input handling
- 📦 Simple and intuitive API
- 🔧 Context manager support for automatic cleanup
- 🌍 Multi-language support (English and Chinese)

## Installation

### From PyPI (when published)
```bash
pip install xbox-controller-py
```

### From Source
```bash
git clone https://github.com/cnctem/XboxControllerPy.git
cd XboxControllerPy
pip install -e .
```

### Requirements
- Python 3.6+
- pygame 2.0.0+

## Quick Start

### Basic Usage
```python
from xbox_controller import XboxController
import time

# Create controller instance
controller = XboxController()

# Connect to controller
controller.connect()

# Get controller info
info = controller.get_controller_info()
print(f"Connected to: {info['name']}")

# Read controller state
while True:
    state = controller.update_state()
    print(f"Left Stick: {state['left_joystick']}")
    print(f"Right Stick: {state['right_joystick']}")
    print(f"Triggers: {state['triggers']}")
    print(f"Buttons: {state['pressed_buttons']}")
    time.sleep(0.1)

# Disconnect when done
controller.disconnect()
```

### Context Manager (Recommended)
```python
from xbox_controller import XboxController

# Automatic connection and cleanup
with XboxController() as controller:
    info = controller.get_controller_info()
    print(f"Device: {info['name']}")
    
    # Use controller...
    state = controller.get_state()
    # Controller automatically disconnects when exiting the context
```

## API Reference

### XboxController Class

#### Methods

- `connect(controller_index=0)`: Connect to Xbox controller
- `disconnect()`: Disconnect from controller
- `get_controller_info()`: Get controller information
- `update_state()`: Update and get current controller state
- `get_state()`: Get current controller state without updating
- `get_formatted_state()`: Get formatted controller state for display

#### Properties

- `connected`: Boolean indicating connection status

### Utility Functions

- `format_axis_value(value)`: Format axis value to 3 decimal places
- `get_controller_state(joystick, buttons, axes)`: Get state from raw data
- `get_button_name(button_id)`: Get button name from ID
- `get_pressed_button_names(buttons)`: Get list of pressed button names

## Examples

Check out the `examples/` directory for more detailed examples:

- `basic_usage.py`: Basic controller reading
- `context_manager.py`: Using context manager
- `event_handling.py`: Event-based input handling

Run examples:
```bash
python examples/basic_usage.py
python examples/context_manager.py
python examples/event_handling.py
```

## Controller Layout

### Button Mapping
- **Buttons 0-3**: A, B, X, Y
- **Buttons 4-5**: LB, RB (Shoulder buttons)
- **Buttons 6-7**: Back, Start
- **Buttons 8-9**: Left Stick, Right Stick (Click)
- **Buttons 12-15**: D-pad (Up, Down, Left, Right)

### Axis Mapping
- **Axes 0-1**: Left Joystick (X, Y)
- **Axes 2-3**: Right Joystick (X, Y)
- **Axes 4-5**: Left Trigger, Right Trigger

## Error Handling

The package includes proper error handling for common scenarios:

```python
try:
    controller = XboxController()
    controller.connect()
    # Use controller...
except SystemExit as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    controller.disconnect()
```

## Development

### Setup Development Environment
```bash
git clone https://github.com/cnctem/XboxControllerPy.git
cd XboxControllerPy
pip install -e .[dev]
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black xbox_controller/
flake8 xbox_controller/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Basic controller connection and state reading
- Context manager support
- Event handling examples
- Multi-language documentation

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the examples in the `examples/` directory

## Roadmap

- [ ] Support for multiple controllers
- [ ] Advanced vibration/haptic feedback
- [ ] Configuration file support
- [ ] GUI control panel
- [ ] Web-based controller monitor
- [ ] Support for other controller types