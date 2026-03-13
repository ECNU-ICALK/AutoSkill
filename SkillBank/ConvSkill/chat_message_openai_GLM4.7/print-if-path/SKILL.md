---
id: "fcf1d17f-b932-4a43-a772-a271fb36c35b"
name: "print / if / path"
description: "General SOP for common requests related to print, if, path."
version: "0.1.0"
tags:
  - "print"
  - "if"
  - "path"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# print / if / path

General SOP for common requests related to print, if, path.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) auto（默认）、txt、ocr（仅用于 pipeline 与 hybrid* 后端
2) b, --backend [pipeline|hybrid-auto-engine|hybrid-http-client|vlm-auto-engine|vlm-http-client
3) 解析后端（默认为 hybrid-auto-engine
4) l, --lang [ch|ch_server|ch_lite|en|korean|japan|chinese_cht|ta|te|ka|th|el|latin|arabic|east_slavic|cyrillic|devanagari
5) 指定文档语言（可提升 OCR 准确率，仅用于 pipeline 与 hybrid* 后端
6) u, --url TEXT                  当使用 http-client 时，需指定服务地址
7) s, --start INTEGER             开始解析的页码（从 0 开始
8) e, --end INTEGER               结束解析的页码（从 0 开始
9) f, --formula BOOLEAN           是否启用公式解析（默认开启
10) t, --table BOOLEAN             是否启用表格解析（默认开启

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
