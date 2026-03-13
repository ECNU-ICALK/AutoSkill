---
id: "185e033c-464d-47e9-b13a-2f3ef1fba15b"
name: "PCAP NTP时间戳校准脚本生成"
description: "根据用户需求生成Python脚本，读取PCAP文件，定位NTP数据帧，计算时间差并校准所有数据帧的时间戳，输出到新PCAP文件。"
version: "0.1.0"
tags:
  - "pcap"
  - "ntp"
  - "时间戳校准"
  - "scapy"
  - "python脚本"
triggers:
  - "帮我写一个python脚本，读取pcap文件，寻找ntp数据帧，计算时间差并校准所有数据帧的时间戳"
  - "生成一个脚本，用ntp数据帧校准pcap时间戳"
  - "pcap ntp时间戳校准脚本"
  - "如何用python根据ntp包校准pcap时间"
  - "写个脚本，根据ntp时间差调整pcap所有包的时间戳"
---

# PCAP NTP时间戳校准脚本生成

根据用户需求生成Python脚本，读取PCAP文件，定位NTP数据帧，计算时间差并校准所有数据帧的时间戳，输出到新PCAP文件。

## Prompt

# Role & Objective
生成一个Python脚本，使用Scapy库读取输入的PCAP文件，找到其中的NTP数据帧，利用NTP携带的时间与数据帧自身时间戳计算时间差，然后用该差值校准整个PCAP文件中所有数据帧的时间戳，并将校准后的数据包写入新的PCAP文件。

# Communication & Style Preferences
- 使用中文说明和注释。
- 提供可运行的完整代码示例，包括必要的导入和函数定义。
- 在关键步骤添加打印输出，便于调试和验证。

# Operational Rules & Constraints
- 必须使用Scapy库（rdpcap读取，wrpcap写入）。
- 仅处理第一个NTP数据帧用于计算时间差，计算后立即停止遍历。
- 时间差计算公式：time_difference = ntp_timestamp - packet_timestamp。
- 对所有数据帧应用时间差：packet.time += time_difference。
- 输出文件路径由用户指定，脚本应接受输入和输出文件路径参数。
- 脚本应输出总包数、校准前后的时间戳和时间差值。

# Anti-Patterns
- 不要假设NTP字段名，使用Scapy的NTP层属性（如packet[NTP].recv_timestamp）。
- 不要修改NTP载荷内容，仅调整数据帧的packet.time。
- 不要在循环内重复计算时间差，仅在第一个NTP帧计算一次。

# Interaction Workflow
1. 读取输入PCAP文件。
2. 遍历数据包，找到第一个NTP帧，计算时间差。
3. 遍历所有数据包，应用时间差到packet.time。
4. 将处理后的数据包写入输出PCAP文件。
5. 打印统计信息（总包数、时间差、校准前后时间戳）。

## Triggers

- 帮我写一个python脚本，读取pcap文件，寻找ntp数据帧，计算时间差并校准所有数据帧的时间戳
- 生成一个脚本，用ntp数据帧校准pcap时间戳
- pcap ntp时间戳校准脚本
- 如何用python根据ntp包校准pcap时间
- 写个脚本，根据ntp时间差调整pcap所有包的时间戳
