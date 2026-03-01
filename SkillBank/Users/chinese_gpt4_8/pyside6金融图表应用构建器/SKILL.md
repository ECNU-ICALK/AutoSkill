---
id: "8c64a14d-e986-4213-8edd-98099fbaefbb"
name: "PySide6金融图表应用构建器"
description: "使用PySide6构建包含mplfinance图表的金融应用，支持时间选择、图表类型切换、键盘事件和暗黑主题"
version: "0.1.0"
tags:
  - "PySide6"
  - "mplfinance"
  - "金融图表"
  - "暗黑主题"
  - "K线图"
triggers:
  - "创建PySide6金融图表应用"
  - "集成mplfinance到PySide6"
  - "构建带时间选择的K线图应用"
  - "PySide6暗黑主题金融界面"
  - "实现键盘控制的图表切换"
---

# PySide6金融图表应用构建器

使用PySide6构建包含mplfinance图表的金融应用，支持时间选择、图表类型切换、键盘事件和暗黑主题

## Prompt

# Role & Objective
构建一个PySide6金融图表应用，集成mplfinance绘图功能，提供完整的用户交互界面和数据查询机制。

# Communication & Style Preferences
- 使用中文界面和提示
- 采用暗黑主题设计
- 支持全屏显示模式
- 组件布局从顶部开始排列

# Operational Rules & Constraints
1. 创建MplfinanceWidget类继承QWidget
2. 必须包含以下UI组件：
   - QDateEdit时间选择器
   - QRadioButton单选框（Candle/Line图表类型）
   - QLineEdit文本输入框
   - QPushButton更新按钮
   - FigureCanvas用于显示mplfinance图表
3. 实现键盘左右箭头事件绑定
4. 使用QVBoxLayout并确保从顶部开始布局
5. 应用暗黑主题：黑色背景、白色字体、灰色边框
6. 支持全屏模式切换
7. 实现FigureCanvas图表更新机制
8. 提供日期递减查询历史数据功能

# Anti-Patterns
- 不要使用默认的亮色主题
- 不要居中对齐布局元素
- 不要忽略键盘事件处理
- 不要在更新图表时创建新的Figure对象

# Interaction Workflow
1. 初始化时创建所有UI组件并设置暗黑主题
2. 用户选择日期和图表类型后点击更新按钮
3. 查询历史数据，如果为空则日期递减继续查询
4. 使用mplfinance绘制图表到FigureCanvas
5. 支持键盘左右箭头切换日期
6. 提供全屏/窗口模式切换功能

## Triggers

- 创建PySide6金融图表应用
- 集成mplfinance到PySide6
- 构建带时间选择的K线图应用
- PySide6暗黑主题金融界面
- 实现键盘控制的图表切换
