---
id: "97cec04a-fc00-4cc7-8746-ea5cbf3979bc"
name: "shadowsocks / mock / list"
description: "General SOP for common requests related to shadowsocks, mock, list."
version: "0.1.0"
tags:
  - "shadowsocks"
  - "mock"
  - "list"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# shadowsocks / mock / list

General SOP for common requests related to shadowsocks, mock, list.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 1. 首先下载 Shadowsocks 客户端，可以在 Github 上搜索 "Shadowsocks" 找到最新的版本
2) 2. 安装客户端后，打开 Shadowsocks，进入主界面，点击右下角的"+"按钮，添加服务器配置
3) 3. 在服务器配置中，依次输入服务器地址、服务器端口、密码以及加密方式，并勾选"UDP Relay"和"OTA"以提升速度和安全性。点击"确定"保存
4) 4. 在主界面上，点击已保存的配置，进入代理模式选择页面。选择"自动模式"或"全局模式"。如果需要自定义规则，则选择"绕过中国大陆和局域网地址"，并自定义需要翻墙的网站或应用
5) 5. 最后点击"开启"按钮，开启 Shadowsocks 代理，即可访问被屏蔽的网站或应用了
6) 注意：需要在 Shadowsocks 的配置中输入正确的服务器地址、端口和密码等信息。如果连接失败，可以尝试更换服务器或更改加密方式
7) user] 服务器地址什么
8) assistant] 服务器地址指的是 Shadowsocks 服务器的 IP 地址，如果你没有自己的服务器，需要购买或者使用免费的 Shadowsocks 服务器。一般来说，购买的服务提供商会提供服务器地址、端口、密码和加密方式等信息，你需要将这些信息输入到 Shadowsocks 客户端的服务器配置中。如果使用免费服务，则需要自行搜索相关信息并输入到客户端中。注意，免费服务有一定的风险，可能存在速度较慢、不稳定、安全性差等问题，建议仅作为临时解决方案，不要长期使用
9) user] 免费的服务地址有哪些
10) assistant] 由于免费的 Shadowsocks 服务器往往会不稳定、速度较慢、存在安全风险等问题，同时由于政策原因也不建议使用免费的服务。这里提供几个比较常见的免费的 Shadowsocks 服务器地址

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
