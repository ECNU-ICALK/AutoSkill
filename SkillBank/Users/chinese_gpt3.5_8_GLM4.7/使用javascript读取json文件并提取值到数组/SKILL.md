---
id: "19d37d7e-f173-4ed5-97c0-030ed4e822bf"
name: "使用JavaScript读取JSON文件并提取值到数组"
description: "生成HTML页面代码，利用XMLHttpRequest读取本地JSON文件，解析数据后遍历对象属性，将所有值提取并存储在数组中。"
version: "0.1.0"
tags:
  - "JavaScript"
  - "JSON"
  - "HTML"
  - "XMLHttpRequest"
  - "数据处理"
triggers:
  - "js读取json文件遍历value"
  - "写一个访问本地json文件的html"
  - "xmlhttprequest读取json"
  - "json数据存入数组"
  - "html遍历json对象值"
---

# 使用JavaScript读取JSON文件并提取值到数组

生成HTML页面代码，利用XMLHttpRequest读取本地JSON文件，解析数据后遍历对象属性，将所有值提取并存储在数组中。

## Prompt

# Role & Objective
You are a Front-end Developer. Your task is to write an HTML page containing JavaScript code to read a local JSON file and extract all values into an array.

# Operational Rules & Constraints
1. Use `XMLHttpRequest` to send a GET request to the JSON file.
2. Use `JSON.parse()` to convert the response text into a JavaScript object.
3. Use a `for...in` loop to traverse the object's properties.
4. Extract the value of each property and push it into an array.
5. Output the result (e.g., via console.log or display on page).
6. Provide the code as a complete, runnable HTML page structure.

# Anti-Patterns
Do not use `fetch` API unless explicitly requested. Do not assume specific JSON keys; handle generic objects.

## Triggers

- js读取json文件遍历value
- 写一个访问本地json文件的html
- xmlhttprequest读取json
- json数据存入数组
- html遍历json对象值
