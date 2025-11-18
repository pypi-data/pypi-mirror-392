# XboxControllerPy

一个使用pygame读取和处理Xbox手柄输入的Python包。

主包用盖世小鸡启明星测试的，绝对不是炫耀哈，券后49r真的很便宜。
```python
button_names = {
    0: "A", 1: "B", 2: "X", 3: "Y",
    4: "方框", 5: "开始", 6: "菜单", 
    7: "左摇杆", 8: "右摇杆", 9: "LB", 10: "RB", 
    11: "上", 12: "下", 13: "左", 14: "右",
    15: "o"
}   # 盖世小鸡启明星1代
```

## 功能特性

- 🎮 简单的Xbox手柄连接和管理
- 🕹️ 实时读取摇杆和按键状态
- 🔫 支持扳机按键
- 🎯 基于事件的输入处理
- 📦 简单直观的API
- 🔧 支持上下文管理器自动清理
- 🌍 多语言支持（英文和中文）

## 安装

### pip 安装（若已发布）
```bash
pip install xbox-controller-py
```

### 从源码安装
```bash
git clone https://github.com/cnctem/XboxControllerPy.git
cd XboxControllerPy
pip install -e .
```

### 依赖要求
- Python 3.6+
- pygame 2.0.0+

---
\* *下面开始都是 Kimi-K2 写的*

## 快速开始

### 基本用法
```python
from xbox_controller import XboxController
import time

# 创建控制器实例
controller = XboxController()

# 连接控制器
controller.connect()

# 获取控制器信息
info = controller.get_controller_info()
print(f"已连接到: {info['name']}")

# 读取控制器状态
while True:
    state = controller.update_state()
    print(f"左摇杆: {state['left_joystick']}")
    print(f"右摇杆: {state['right_joystick']}")
    print(f"扳机: {state['triggers']}")
    print(f"按键: {state['pressed_buttons']}")
    time.sleep(0.1)

# 断开连接
controller.disconnect()
```

### 上下文管理器（推荐）
```python
from xbox_controller import XboxController

# 自动连接和清理
with XboxController() as controller:
    info = controller.get_controller_info()
    print(f"设备: {info['name']}")
    
    # 使用控制器...
    state = controller.get_state()
    # 退出上下文时控制器自动断开连接
```

## API参考

### XboxController类

#### 方法

- `connect(controller_index=0)`: 连接Xbox手柄
- `disconnect()`: 断开手柄连接
- `get_controller_info()`: 获取手柄信息
- `update_state()`: 更新并获取当前手柄状态
- `get_state()`: 获取当前手柄状态（不更新）
- `get_formatted_state()`: 获取格式化的手柄状态用于显示

#### 属性

- `connected`: 布尔值，表示连接状态

### 工具函数

- `format_axis_value(value)`: 将轴值格式化为3位小数
- `get_controller_state(joystick, buttons, axes)`: 从原始数据获取状态
- `get_button_name(button_id)`: 根据ID获取按键名称
- `get_pressed_button_names(buttons)`: 获取按下的按键名称列表

## 示例

查看 `examples/` 目录获取更多详细示例：

- `basic_usage.py`: 基本的手柄读取
- `context_manager.py`: 使用上下文管理器
- `event_handling.py`: 基于事件的输入处理

运行示例：
```bash
python examples/basic_usage.py
python examples/context_manager.py
python examples/event_handling.py
```

## 手柄布局（参考启明星1代）

### 按键映射
- **按键 0-3**: A, B, X, Y
- **按键 4-5**: LB, RB（肩键）
- **按键 6-7**: 返回, 开始
- **按键 8-9**: 左摇杆, 右摇杆（按压）
- **按键 12-15**: 方向键（上, 下, 左, 右）

### 轴映射
- **轴 0-1**: 左摇杆（X, Y）
- **轴 2-3**: 右摇杆（X, Y）
- **轴 4-5**: 左扳机, 右扳机

## 错误处理

包中包含对常见情况的适当错误处理：

```python
try:
    controller = XboxController()
    controller.connect()
    # 使用控制器...
except SystemExit as e:
    print(f"连接错误: {e}")
except Exception as e:
    print(f"错误: {e}")
finally:
    controller.disconnect()
```

## 开发

### 设置开发环境
```bash
git clone https://github.com/cnctem/XboxControllerPy.git
cd XboxControllerPy
pip install -e .[dev]
```

### 运行测试
```bash
pytest
```

### 代码格式化
```bash
black xbox_controller/
flake8 xbox_controller/
```

## 贡献

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v1.0.0
- 初始版本
- 基本的手柄连接和状态读取
- 支持上下文管理器
- 事件处理示例
- 多语言文档

## 支持

如果遇到任何问题或有疑问：
- 在 GitHub 上打开 issue
- 查看现有 issue 寻找解决方案
- 查看 `examples/` 目录中的示例

## 愿意做就提PR吧，相信你们的智慧