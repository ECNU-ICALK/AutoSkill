---
id: "b5d1cfe1-cbd2-4543-971b-b3daec9b9697"
name: "ax / np / method"
description: "General SOP for common requests related to ax, np, method."
version: "0.1.0"
tags:
  - "ax"
  - "np"
  - "method"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# ax / np / method

General SOP for common requests related to ax, np, method.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 保留原文的同时，用开源 MT 模型（如 facebook/wmt19-ru-en）生成英文并行版；后续训练时中英优先，俄文作为可选项。\n\n3. 任务格式对齐  \n   目标格式：{\"dialogs\": [{\"role\":\"user\",\"content\":Q}, {\"role\":\"assistant\",\"content\":A}]}  \n   3.1 Vikhrmodels/physics_big  \n       - 将 text 字段作为 Q，answer 字段内 solution.text 作为 A；若 answer 含数值结果，在 A 末尾追加 “最终答案：\\(\\boxed{数值}\\)”。  \n   3.2 camel-ai/physics  \n       - message_1
2) Q，message_2
3) A；若单条样本 token>2048，按段落拆成多轮（user:“请继续”，assistant:剩余内容）。  \n   3.3 jeffmeloy/sonnet3.5_science_conversations  \n       - 每轮 human
4) user，gpt
5) assistant；合并连续 gpt 轮次为单条 assistant 内容，保证不超过 2048 token。  \n   3.4 STEM-AI-mtl/Electrical-engineering  \n       - instruction+input 拼接成 Q（input 为空则只用 instruction），output 作为 A。  \n   3.5 tasksource/ScienceQA_text_only  \n       - 将 lecture 与 question 拼接为上下文，choices 列成 A/B/C/D，构造 Q：  \n         “【阅读材料】…\\n【问题】…\\n选项：A… B… C… D…\\n请直接给出正确选项字母。”  \n         A：solution 字段内容，并以 “正确答案：A” 结尾。  \n   3.6 hfl/stem_zh_instruction  \n       - instruction+input
6) Q，output
7) A，无需额外处理。\n\n4. 数据清洗  \n   4.1 去重：按标准化后的 Q 文本（去空格、统一 LaTeX 命令）计算 MinHash，Jaccard>0.9 视为重复，仅保留最长答案。  \n   4.2 过滤：  \n       - 若 A 缺失或长度<20 字符，丢弃；  \n       - 若 Q 含图片外链或无法解析的 OCR 乱码，丢弃；  \n       - 用规则过滤明显非物理内容（如“日语语法”“法国历史”关键词）。  \n   4.3 公式完整性检查：用正则统计未闭合的“\\(”或“\\[”，比例>5 % 的样本人工抽查或丢弃。\n\n5. 质量打分与排序（可选 LLM 推理）  \n   5.1 随机抽取 2 k 样本，用 gpt-3.5-turbo 打分：  \n       prompt = f\"\"\"请判断以下物理问答是否准确、步骤清晰、无科学错误，1-5 分，仅返回数字。\\nQ：{Q}\\nA：{A}\"\"\"  \n   5.2 将平均分<3 的样本整批降权或丢弃，保留高分样本。\n\n6. 中文增强（可选 LLM 合成）  \n   6.1 从英文高分样本中随机选 3 k，用如下 prompt 生成中文平行样本：  \n       prompt = f\"\"\"把下列英文物理题与解答翻译成地道中文，保留 LaTeX 公式不变，语言符合大陆教材习惯。\\n{英文 Q&A}\"\"\"  \n   6.2 人工抽检 100 条，准确率≥95 % 才合并入主集。\n\n7. 最终合并与划分  \n   7.1 将上述所有合格样本合并，打乱后按 95/5 分割为 train/val。  \n   7.2 输出两个 jsonl 文件，每行一条 {\"dialogs\": [...]}，可直接喂入 SFT trainer
8) python
9) data-processing code block
10) import re

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
