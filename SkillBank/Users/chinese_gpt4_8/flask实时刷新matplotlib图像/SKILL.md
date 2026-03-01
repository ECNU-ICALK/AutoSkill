---
id: "27da421a-a116-4cb1-86c4-8a0112eb8e27"
name: "Flask实时刷新Matplotlib图像"
description: "使用Flask、Flask-Caching和APScheduler实现Matplotlib图像的后台定时更新，图像存储在缓存中，前端通过JavaScript定时刷新显示，支持毫秒级刷新间隔配置"
version: "0.1.0"
tags:
  - "Flask"
  - "Matplotlib"
  - "实时刷新"
  - "缓存"
  - "APScheduler"
triggers:
  - "Flask实时刷新图像"
  - "Matplotlib定时更新"
  - "Flask缓存图像显示"
  - "后台更新图表"
  - "毫秒级刷新间隔"
---

# Flask实时刷新Matplotlib图像

使用Flask、Flask-Caching和APScheduler实现Matplotlib图像的后台定时更新，图像存储在缓存中，前端通过JavaScript定时刷新显示，支持毫秒级刷新间隔配置

## Prompt

# Role & Objective
实现一个Flask应用，能够后台定时更新Matplotlib绘制的折线图，图像存储在Flask-Caching缓存中，前端页面通过JavaScript定时刷新显示最新图像，支持毫秒级刷新间隔配置。

# Communication & Style Preferences
- 使用中文进行代码注释和说明
- 代码结构清晰，关键步骤添加注释
- 前端使用原生JavaScript，避免依赖外部库

# Operational Rules & Constraints
1. 必须使用Flask-Caching存储图像数据，不保存到本地文件
2. 使用APScheduler的BackgroundScheduler实现后台定时任务
3. Matplotlib必须使用Agg后端，避免线程安全问题
4. 图像更新函数必须使用线程锁保证线程安全
5. 前端JavaScript必须添加时间戳或随机参数防止浏览器缓存
6. 支持通过seconds参数的小数设置毫秒级刷新间隔
7. 应用启动时必须初始化缓存中的图像
8. 路由/plot.png返回缓存中的图像数据
9. 路由/返回index.html模板

# Anti-Patterns
- 不要将图像保存到本地文件系统
- 不要在每次请求时重新生成图像
- 不要使用Flask的自动重载功能（use_reloader=False）
- 不要忽略线程安全问题
- 不要在前端使用固定的图像URL

# Interaction Workflow
1. 初始化Flask应用和缓存配置
2. 设置Matplotlib为Agg后端
3. 定义全局数据存储和线程锁
4. 实现update_image函数：更新数据、绘图、存储到缓存
5. 配置APScheduler定时任务调用update_image
6. 实现plot_png路由：从缓存获取图像数据并返回
7. 实现index路由：返回HTML模板
8. 创建index.html模板：包含JavaScript定时刷新逻辑
9. 启动应用时初始化缓存图像

## Triggers

- Flask实时刷新图像
- Matplotlib定时更新
- Flask缓存图像显示
- 后台更新图表
- 毫秒级刷新间隔
