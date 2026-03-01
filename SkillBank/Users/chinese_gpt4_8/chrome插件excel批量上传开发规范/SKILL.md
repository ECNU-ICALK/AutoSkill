---
id: "c1066e99-9148-4610-a1fa-a8dd63be687e"
name: "Chrome插件Excel批量上传开发规范"
description: "用于开发Chrome Manifest V3插件，实现Excel文件解析、ICCID数据分批上传、延时控制、请求格式化等可复用流程"
version: "0.1.0"
tags:
  - "Chrome插件"
  - "Manifest V3"
  - "Excel导入"
  - "分批上传"
  - "ICCID"
triggers:
  - "开发Chrome插件批量上传Excel"
  - "Chrome插件分批上传ICCID"
  - "Manifest V3 Excel导入插件"
  - "Chrome插件multipart/form-data上传"
  - "Excel数据分批延时上传"
---

# Chrome插件Excel批量上传开发规范

用于开发Chrome Manifest V3插件，实现Excel文件解析、ICCID数据分批上传、延时控制、请求格式化等可复用流程

## Prompt

# Role & Objective
开发Chrome Manifest V3插件，实现Excel文件导入，按每1000条分批上传ICCID数据到目标网站，使用multipart/form-data格式，包含延时控制和响应处理。

# Communication & Style Preferences
使用中文编写代码注释和提示信息，控制台输出使用英文，用户提示使用中文。

# Operational Rules & Constraints
1. 使用xlsx.core.min.js解析Excel文件
2. Excel格式要求：第一行第一列为iccid标题
3. 批次大小固定为1000条
4. 上传时将iccid存储为文本文件，每行一个iccid值
5. 使用multipart/form-data格式，字段名：loadfile（文件）和_dataField（空JSON对象）
6. 文件名固定为GJP_1000_1.txt，MIME类型为text/plain
7. 循环上传时每批次间隔3秒
8. 使用fetch API，设置credentials: 'include'携带cookie
9. 响应必须使用response.text()解析为字符串并通过alert显示
10. Manifest V3必须使用service_worker替代background.page
11. 使用action替代browser_action
12. 权限分离：permissions和host_permissions

# Anti-Patterns
- 不使用jQuery.ajax，改用fetch API
- 不手动拼接multipart字符串，使用FormData
- 不使用async:false，改用async/await
- 不在V3中使用webRequestBlocking权限

# Interaction Workflow
1. 用户选择Excel文件
2. 解析Excel提取iccid列
3. 按批次分割数据
4. 循环上传每批次，间隔3秒
5. 解析响应并提示用户

## Triggers

- 开发Chrome插件批量上传Excel
- Chrome插件分批上传ICCID
- Manifest V3 Excel导入插件
- Chrome插件multipart/form-data上传
- Excel数据分批延时上传
