import pygame
import time
import sys
from .utils import format_axis_value

class XboxController:
    """
    Xbox Controller class for handling Xbox controller input.
    
    This class provides methods to initialize controller connection,
    read controller state, and handle controller events.
    """
    
    def __init__(self):
        """Initialize Xbox Controller"""
        self.joystick = None
        self.buttons = {}
        self.axes = {}
        self.connected = False
        
    def connect(self, controller_index=0):
        """
        Connect to Xbox controller
        
        Args:
            controller_index (int): Index of controller to connect to (default: 0)
            
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            SystemExit: If no controller is detected
        """
        pygame.init()
        pygame.joystick.init()
        
        # 检查是否有手柄连接
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            raise SystemExit("未检测到任何手柄设备!")
        
        if controller_index >= joystick_count:
            raise ValueError(f"控制器索引 {controller_index} 超出范围，检测到 {joystick_count} 个控制器")
        
        # 使用指定手柄
        self.joystick = pygame.joystick.Joystick(controller_index)
        self.joystick.init()
        
        # 初始化按键和摇杆状态
        self.buttons = {i: False for i in range(self.joystick.get_numbuttons())}
        self.axes = {i: 0.0 for i in range(self.joystick.get_numaxes())}
        
        self.connected = True
        return True
    
    def disconnect(self):
        """Disconnect from controller and cleanup resources"""
        if self.connected:
            pygame.joystick.quit()
            pygame.quit()
            self.connected = False
            self.joystick = None
    
    def get_controller_info(self):
        """
        Get controller information
        
        Returns:
            dict: Controller information including name, ID, button count, and axis count
        """
        if not self.connected:
            return {"connected": False}
            
        return {
            "connected": True,
            "name": self.joystick.get_name(),
            "id": self.joystick.get_id(),
            "button_count": self.joystick.get_numbuttons(),
            "axis_count": self.joystick.get_numaxes()
        }
    
    def update_state(self):
        """
        Update controller state by processing pygame events
        
        Returns:
            dict: Updated controller state
        """
        if not self.connected:
            return {"connected": False}
        
        # 处理pygame事件
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                self.buttons[event.button] = True
            elif event.type == pygame.JOYBUTTONUP:
                self.buttons[event.button] = False
            elif event.type == pygame.JOYAXISMOTION:
                self.axes[event.axis] = event.value
        
        return self.get_state()
    
    def get_state(self):
        """
        Get current controller state
        
        Returns:
            dict: Current controller state including joysticks, triggers, and buttons
        """
        if not self.connected:
            return {"connected": False}
        
        # 获取摇杆状态
        left_joystick = [self.axes.get(0, 0), self.axes.get(1, 0)]  # 左摇杆 X, Y
        right_joystick = [self.axes.get(2, 0), self.axes.get(3, 0)]  # 右摇杆 X, Y
        triggers = [self.axes.get(4, 0), self.axes.get(5, 0)]  # 左扳机, 右扳机
        
        # 获取按下的按键
        pressed_buttons = []
        for button_id, state in self.buttons.items():
            if state:
                pressed_buttons.append(button_id)
        
        return {
            "connected": True,
            "left_joystick": left_joystick,
            "right_joystick": right_joystick,
            "triggers": triggers,
            "pressed_buttons": pressed_buttons
        }
    
    def get_formatted_state(self):
        """
        Get formatted controller state for display
        
        Returns:
            dict: Formatted controller state with formatted axis values
        """
        state = self.get_state()
        if not state["connected"]:
            return state
        
        return {
            "connected": True,
            "left_joystick": [format_axis_value(val) for val in state["left_joystick"]],
            "right_joystick": [format_axis_value(val) for val in state["right_joystick"]],
            "triggers": [format_axis_value(val) for val in state["triggers"]],
            "pressed_buttons": state["pressed_buttons"]
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def get_controller_state(joystick, buttons, axes):
    """
    Get controller state from raw joystick data
    
    Args:
        joystick: Pygame joystick object
        buttons: Dictionary of button states
        axes: Dictionary of axis values
        
    Returns:
        tuple: (left_joystick, right_joystick, triggers, pressed_buttons)
    """
    # 获取摇杆状态
    left_joystick = [axes.get(0, 0), axes.get(1, 0)]  # 左摇杆 X, Y
    right_joystick = [axes.get(2, 0), axes.get(3, 0)]  # 右摇杆 X, Y
    triggers = [axes.get(4, 0), axes.get(5, 0)]  # 左扳机, 右扳机
    
    # 获取按下的按键
    pressed_buttons = []
    for button_id, state in buttons.items():
        if state:
            pressed_buttons.append(button_id)
    
    return left_joystick, right_joystick, triggers, pressed_buttons