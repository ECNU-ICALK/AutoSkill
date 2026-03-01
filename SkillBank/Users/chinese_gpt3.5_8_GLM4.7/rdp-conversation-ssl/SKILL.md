---
id: "6522297f-f80c-4f67-9d68-7083ab89e6d3"
name: "rdp / conversation / ssl"
description: "General SOP for common requests related to rdp, conversation, ssl."
version: "0.1.0"
tags:
  - "rdp"
  - "conversation"
  - "ssl"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# rdp / conversation / ssl

General SOP for common requests related to rdp, conversation, ssl.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: 1b9d93bb5b4591ff97b67f623c3c3600.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) 现在想写一个互联网暴露面资产网络安全运营规范，请问以下内容还有哪些需要完善的地方：第三十二条 	各互联网暴露面应落实日志留存相关要求，定期进行日志审计，及时发现异常行为并开展核查处置。
8) (一)日志留存。互联网暴露资产应完成日志采集能力100% 部署，日志留存时间不得少于 6 个月。
9) (二)日志集中纳管。互联网暴露资产的登陆日志、操作日志、告警日志、中间件等关键日志信息应集中采集统一管理。应推进安全防护组件(包含不限于防火墙、IPS/IDS、WAF、全流量、4A)日志的集中采集和关联分析。
10) (三)日志审计。推进安全日志审计能力建设，明确日志审计责任人，应每月执行日志审计并形成审计报告存档备查。

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
