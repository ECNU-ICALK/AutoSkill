---
id: "2480c60e-c735-4bb1-a3e6-e7e597d3f360"
name: "Python Tkinter Treeview Excel交互式表格查看器"
description: "使用Python Tkinter Treeview组件读取Excel文件，实现点击列头排序、添加动态行序号、双击单元格弹窗显示内容以及自定义列宽的功能。"
version: "0.1.0"
tags:
  - "Python"
  - "Tkinter"
  - "Treeview"
  - "Excel"
  - "GUI"
triggers:
  - "tkinter treeview excel 排序"
  - "python treeview 双击弹窗"
  - "tkinter 表格添加序号"
  - "treeview 自定义列宽"
---

# Python Tkinter Treeview Excel交互式表格查看器

使用Python Tkinter Treeview组件读取Excel文件，实现点击列头排序、添加动态行序号、双击单元格弹窗显示内容以及自定义列宽的功能。

## Prompt

# Role & Objective
编写Python脚本，使用Tkinter的Treeview组件读取Excel文件并在窗口中显示。

# Operational Rules & Constraints
1. **数据加载**: 使用pandas读取Excel文件。
2. **表格显示**: 使用ttk.Treeview组件，配置垂直滚动条。
3. **排序功能**: 点击列标题时，根据该列对表格数据进行排序（升序/降序切换）。
4. **序号列**: 在数据列前添加一个序号列（'#0'），显示行号。排序后序号需重新计算以反映当前顺序。
5. **双击事件**: 绑定双击事件。双击指定列的单元格时，弹出消息框显示该单元格的内容。需确保弹窗显示的是正确的数据列内容，而非序号列。
6. **列宽配置**: 支持设置每一列的显示宽度。
7. **布局**: 使用place几何管理器定位组件。
8. **对齐**: 确保列标题与数据内容正确对应，无错位。

# Anti-Patterns
- 不要将序号列的数据与实际数据列混淆。
- 不要在双击弹窗中显示序号列的内容，应显示原数据列的内容。
- 不要使用pack或grid进行布局，除非用户明确要求，默认使用place。

## Triggers

- tkinter treeview excel 排序
- python treeview 双击弹窗
- tkinter 表格添加序号
- treeview 自定义列宽
