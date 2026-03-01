---
id: "bb51754d-c74f-47ae-bcfe-a07e92d53ec8"
name: "GPU数据获取函数实现"
description: "实现一个根据GPU位置信息，通过system_ctrl接口获取GPU的ECC计数、错误计数和功率制动状态的函数，支持多种交换机配置，并在获取失败时设置默认值。"
version: "0.1.0"
tags:
  - "GPU监控"
  - "I2C通信"
  - "系统控制接口"
  - "硬件数据采集"
  - "错误处理"
triggers:
  - "实现GPU数据获取函数"
  - "获取GPU的ECC和错误计数"
  - "根据GPU位置获取监控数据"
  - "system_ctrl接口获取GPU状态"
  - "GPU数据采集实现"
---

# GPU数据获取函数实现

实现一个根据GPU位置信息，通过system_ctrl接口获取GPU的ECC计数、错误计数和功率制动状态的函数，支持多种交换机配置，并在获取失败时设置默认值。

## Prompt

# Role & Objective
实现一个可复用的GPU数据获取函数，根据GPU的物理位置（由交换机类型决定），通过system_ctrl接口从不同的I2C总线路径获取ECC计数、错误计数和功率制动状态数据。

# Communication & Style Preferences
- 使用C语言实现
- 函数命名清晰，参数明确
- 代码结构清晰，注释充分

# Operational Rules & Constraints
1. 输入参数：
   - gpu_data结构体指针，用于输出数据
   - gpu_location字符串，表示GPU位置
2. 位置映射规则：
   - 0switch: 位置范围为pcie0-pcie11
   - 2switch: 位置范围为pcie1-pcie13
   - 4switch: 位置范围为pcie0-pcie21
3. 数据获取：
   - 使用system_ctrl接口获取数据
   - ECC count、error count、power brake status来自不同的I2C bus路径
4. 错误处理：
   - 如果获取成功，将数据赋值给gpu_data结构体对应成员
   - 如果获取失败，将对应成员设置为"unknown"
5. 路径构建格式：
   - 使用格式"/device/gpu/{location}/{datatype}"构建I2C路径

# Anti-Patterns
- 不要硬编码具体的PCIe编号，使用位置参数动态构建
- 不要忽略错误处理，必须处理获取失败的情况
- 不要假设数据总是可用，必须有fallback机制

# Interaction Workflow
1. 根据gpu_location构建三个数据路径
2. 依次调用system_ctrl接口获取ECC count、error count、power brake status
3. 检查每次获取的返回值
4. 根据获取结果填充gpu_data结构体或设置"unknown"

## Triggers

- 实现GPU数据获取函数
- 获取GPU的ECC和错误计数
- 根据GPU位置获取监控数据
- system_ctrl接口获取GPU状态
- GPU数据采集实现
