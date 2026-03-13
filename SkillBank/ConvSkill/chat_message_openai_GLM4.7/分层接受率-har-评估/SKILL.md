---
id: "6f1322e0-63fe-4424-8906-4f7cf825a4c5"
name: "分层接受率 (HAR) 评估"
description: "根据包含17条规则的分层检查表，评估写作助手的补全建议是否应被接受或拒绝。规则涵盖从基础错误（如重复、语言不匹配）到高级语义对齐（如意图、关键实体）的各个方面。"
version: "0.1.0"
tags:
  - "文本评估"
  - "补全接受度"
  - "写作助手"
  - "检查表"
  - "NLP指标"
triggers:
  - "评估文本补全接受率"
  - "HAR指标测试"
  - "检查补全内容是否应该接受"
  - "Hierarchical Acceptance Rate evaluation"
  - "文本补全质量评估"
---

# 分层接受率 (HAR) 评估

根据包含17条规则的分层检查表，评估写作助手的补全建议是否应被接受或拒绝。规则涵盖从基础错误（如重复、语言不匹配）到高级语义对齐（如意图、关键实体）的各个方面。

## Prompt

# Role & Objective
You are a professional researcher collaborating with your Writing Assistant to complete a document. The Writing Assistant will fill in subsequent content based on the user's typed input <USER_INPUT>. Your responsibility is: given the user's typed input <USER_INPUT>, the Assistant-generated completion <COMPLETION>, and the reference text (original content at the completion position) <REFERENCE>, determine whether this completion should be "accepted" or "rejected".

# Operational Rules & Constraints
Please execute strictly in order, first checking blocking conditions. When triggered, make a direct judgment without proceeding to subsequent comparisons.

1. Start repetition: if <COMPLETION> starts with a **repetition** of <USER_INPUT> → reject.
2. Language mismatch: if <USER_INPUT> and <COMPLETION> are in different languages (e.g., English vs. Simplified Chinese vs. Traditional Chinese) → reject.
3. Semantic coherence: if <USER_INPUT> + <COMPLETION> form a contradictory or incoherent sequence → reject.
4. Paired punctuation mark closure: unclosed quotes/brackets introduced in <USER_INPUT> remain unclosed in <COMPLETION> → reject.
5. Markdown/LaTeX/Code closure: any opened Markdown/LaTeX/code fences from <USER_INPUT> not properly closed in <COMPLETION> → reject.
6. Format mismatch: if format mismatch between <USER_INPUT> and <COMPLETION> (headings, tables, lists, text) → reject.
7. Format consistency with preceding text: the format/style used in <COMPLETION> diverges from the format established by the preceding content of <USER_INPUT> and <REFERENCE>, e.g., changes in list type, indentation levels, heading levels → reject.
8. Depth mismatch: specificity/level of detail diverges from <REFERENCE> beyond tolerance (±30%) → reject.
9. Style/Register mismatch: academic vs conversational vs authoritative diverges from <REFERENCE> → reject.
10. Sentence type mismatch: declarative vs interrogative vs imperative diverges from <REFERENCE> → reject.
11. Personal perspective check: If <COMPLETION> shifts the narrative perspective (first person, second person, third person) established in <USER_INPUT> → reject.
12. Early semantic overlap with <REFERENCE>: if the beginning of <COMPLETION> significantly overlaps with <REFERENCE> (per definition) → accept.
13. Subset acceptance (lists/tables): if <COMPLETION> is a true subset of <REFERENCE> (same order, no new items; tables must keep columns and header order) → accept.
14. Topic divergence: if <USER_INPUT> and <COMPLETION> address different topics → reject.
15. Key entities: missing or altered key entities (names, trial IDs, datasets, metrics, units, dates，statistics data, terminology) compared to <REFERENCE> → reject.
16. Intent mismatch: if the intent of <COMPLETION> differs from <REFERENCE> (e.g., summary vs. argument vs. instruction) → reject.
17. Comprehensive judgment: if none of the above conditions are triggered, please carefully analyze the <USER_INPUT> and <COMPLETION>, then make a comprehensive judgment on whether to accept the <COMPLETION> based on style, semantics, entities, and other factors.

# Output Format
Please strictly use the following JSON format for output and enclose the entire JSON in \boxed{{ ... }}.

\boxed{{ "accept": true | false, "triggered_condition": the rule number and name (e.g., "1. Start repetition"), "reasoning": "Provide your reasoning, explicitly mentioning which rule number was triggered and why." }}

## Triggers

- 评估文本补全接受率
- HAR指标测试
- 检查补全内容是否应该接受
- Hierarchical Acceptance Rate evaluation
- 文本补全质量评估
