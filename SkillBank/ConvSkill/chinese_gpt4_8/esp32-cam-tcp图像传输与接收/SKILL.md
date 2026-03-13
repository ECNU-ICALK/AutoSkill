---
id: "cd94ee0d-13b8-41a0-903b-518d3ead46bf"
name: "ESP32-CAM TCP图像传输与接收"
description: "实现ESP32-CAM通过TCP发送JPEG图像数据，服务端接收并使用OpenCV显示的完整流程，包含长度前缀协议和错误处理"
version: "0.1.0"
tags:
  - "ESP32-CAM"
  - "TCP"
  - "图像传输"
  - "OpenCV"
  - "MicroPython"
triggers:
  - "esp32cam tcp发送图像"
  - "tcp传输jpeg到opencv"
  - "esp32摄像头网络传输"
  - "tcp图像流接收显示"
  - "micropython tcp图像发送"
---

# ESP32-CAM TCP图像传输与接收

实现ESP32-CAM通过TCP发送JPEG图像数据，服务端接收并使用OpenCV显示的完整流程，包含长度前缀协议和错误处理

## Prompt

# Role & Objective
编写ESP32-CAM端MicroPython程序和服务端Python程序，实现通过TCP传输JPEG图像并在服务端用OpenCV实时显示。必须使用长度前缀协议确保帧边界正确。

# Communication & Style Preferences
使用中文注释，代码结构清晰，关键步骤添加说明。

# Operational Rules & Constraints
1. ESP32-CAM端必须先发送4字节大端序的图像长度，再发送图像数据
2. 服务端必须先接收4字节长度，再按长度接收完整图像
3. 使用socket.SOCK_STREAM建立TCP连接
4. 服务端使用cv2.imdecode解码接收到的JPEG数据
5. 发送端使用time.sleep防止粘包问题
6. 服务端设置SO_REUSEADDR避免端口占用错误
7. 异常处理必须包含ECONNRESET和ENOTCONN的重连逻辑

# Anti-Patterns
- 不要使用UDP相关函数
- 不要省略长度前缀
- 不要在TCP中使用sendto
- 不要忽略字节序一致性

# Interaction Workflow
1. ESP32-CAM初始化相机并连接服务器
2. 循环捕获图像，发送长度+数据
3. 服务端监听连接，接收长度+数据
4. 解码并显示图像
5. 处理网络异常和重连

## Triggers

- esp32cam tcp发送图像
- tcp传输jpeg到opencv
- esp32摄像头网络传输
- tcp图像流接收显示
- micropython tcp图像发送
