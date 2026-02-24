---
id: "39e70450-6375-4074-a522-0897f294b21e"
name: "pet-care-checklist-generator"
description: "Generates two parallel, highly actionable pet care checklists — one for daily owner use and one for temporary caregivers — with strict adherence to simplicity, zero-omission of critical health checks, and execution-first design."
version: "0.1.0"
tags:
  - "checklist"
  - "pet-care"
  - "caregiver-handoff"
  - "health-monitoring"
  - "execution-focused"
triggers:
  - "生成日常和代养两版照护清单"
  - "要简洁可执行的检查表"
  - "不遗漏关键检查点"
  - "宠物代养交接清单"
  - "狗狗照护打卡表"
---

# pet-care-checklist-generator

Generates two parallel, highly actionable pet care checklists — one for daily owner use and one for temporary caregivers — with strict adherence to simplicity, zero-omission of critical health checks, and execution-first design.

## Prompt

# Goal
Generate two de-identified, printable, operationally identical pet care checklists: (1) a daily self-care version for the owner, and (2) a temporary caregiver version — both optimized for clarity, speed of execution (<30 sec per item), and zero omission of non-negotiable health observation points (appetite, stool, spirit, vital redlines).

# Constraints & Style
• Output only two clean markdown tables (no explanations, no intros, no footers): one labeled "【日常自养版】", one labeled "【出差代养版】".
• All items must be concrete, observable actions — no vague terms like "monitor" or "observe"; replace with "□拍空碗照", "□ count bowel movements", "□ check gum color with flashlight".
• Daily checklist: A4-printable, single-page, columnar layout with three sections: '每日必做', '每周定点', '关键记录项' — use minimal shorthand (e.g., `便型3✓`, `体重10.2kg`); omit all proper nouns, dates, doses, or brand names.
• Caregiver checklist:明信片-size equivalent — icon-driven, red-boxed critical actions, ❌-marked forbidden actions, no paragraphs, all text ≤8 words per line; include only what *must* be done *and verified* each day (feeding, walking, appetite/stool/spirit triage, emergency triggers).
• Remove all instance-specific payload: no dog names, cities, weights, brands, drug names, dates, phone numbers, or URLs. Use placeholders like `<DOG_NAME>`, `<EMERGENCY_CONTACT>` only where structurally required for completeness.
• No markdown code blocks, no JSON, no assistant commentary — pure output-ready markdown.
• Absolute brevity: if an item can be shortened without ambiguity, shorten it (e.g., "weigh on Sunday morning" → "周日晨称重").
• Never invent new medical thresholds or protocols — only encode those explicitly user-confirmed (e.g., 3-level appetite rule, Bristol stool reference, gum-color check, 24h拒食 redline).

## Triggers

- 生成日常和代养两版照护清单
- 要简洁可执行的检查表
- 不遗漏关键检查点
- 宠物代养交接清单
- 狗狗照护打卡表
