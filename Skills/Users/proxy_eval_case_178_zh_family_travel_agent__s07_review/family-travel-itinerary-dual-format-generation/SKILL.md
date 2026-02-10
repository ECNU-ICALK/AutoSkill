---
id: "2147d0d2-b9a7-41a7-9781-ddd4d2ca1d6a"
name: "family-travel-itinerary-dual-format-generation"
description: "Generates two synchronized versions of a family travel itinerary: a detailed execution version for planners and a concise, scannable version for family group chats — both aligned on accessibility, weather resilience, low-mobility constraints, and a mandatory post-Day-3 reflection checkpoint with pre-defined adjustment rules."
version: "0.1.1"
tags:
  - "family-travel"
  - "accessibility"
  - "weather-resilience"
  - "multi-format-output"
  - "low-mobility"
  - "operational-rhythm"
triggers:
  - "输出执行版和家庭群简版"
  - "生成两个版本"
  - "要一个详细版和一个发群里的简版"
  - "做一份给管家看、一份给家人看"
  - "增加每周复盘步骤和调整规则"
---

# family-travel-itinerary-dual-format-generation

Generates two synchronized versions of a family travel itinerary: a detailed execution version for planners and a concise, scannable version for family group chats — both aligned on accessibility, weather resilience, low-mobility constraints, and a mandatory post-Day-3 reflection checkpoint with pre-defined adjustment rules.

## Prompt

# Goal
Generate two synchronized itinerary versions for a multi-generational family trip: (1) a full 'Execution Version' with precise logistics, timing, accessibility notes, contingency triggers, and budget/contact integration; and (2) a 'Family Group Chat Version' — ultra-concise, emoji-annotated, time-zone-aware, and stripped of operational jargon — suitable for sharing directly in a messaging app.

# Constraints & Style
• Both versions must reflect the same core constraints: strict daily walking limit (<2,000 steps), mandatory 12:00–14:30 midday rest, zero stairs/uneven surfaces, weather-triggered indoor alternatives (all ≤5-min walk from original site), 高铁-only transport with no red-eye departures, and a mandatory post-Day-3 reflection checkpoint with three-tier adjustment rules (✅ stable → continue; ⚠️ mild fatigue or ≥2 weather disruptions → compress outdoor time by 30 min + add 15 min seated sensory activity; ❌ acute discomfort or ≥3 weather disruptions → activate ‘Reset Day’ with full indoor programming and local delivery).
• Execution Version: structured as a timeline or table; includes exact train numbers, venue accessibility features (e.g., 'elevator to all floors'), real-time resource links (QR-ready), explicit trigger conditions (e.g., '⚠️ Rain >2mm/hr → switch to <MUSEUM_NAME>'), budget line items, emergency contacts, and verification cues (e.g., 'on-site confirmation only, no booking required').
• Family Group Chat Version: max 12 lines; uses only ✅/⚠️/❌/🌧️/😴/🚌/🍵/🎬 emojis for visual scanning; omits URLs, technical terms, internal logic, and numbers overload; highlights *what* happens *when*, *where*, *why it’s safe/easy*, and *who to message* — e.g., '😴 12–2:30 PM: Hotel nap — knee-friendly beds & quiet floor'; '🍵 3:00 PM: Seated tea tasting — no standing, no stairs'.
• Never invent venues, transport options, policies, thresholds, or contacts. All indoor alternatives, emergency protocols, and adjustment rules must derive exclusively from user-specified needs and prior-confirmed options (e.g., '老人膝盖不好', '如遇天气变化', '<HOTEL_BRAND> has elevator access').
• De-identify all location names, vendor names, and personal identifiers — use placeholders like <CITY>, <MUSEUM_NAME>, <HOTEL_BRAND>, <DATE>, <VERSION>.
• Output both versions in the same language as user input; no markdown tables in Family Version — use line breaks and spacing only; label sections as '## 🌟【执行版】' and '## 📱【家庭群简版】' — no additional commentary or summaries.

# Workflow
1. Confirm departure city and traveler mobility profile (e.g., '72yo, walks with cane; 5yo, high energy').
2. Map all outdoor activities to pre-vetted indoor alternatives within 5-minute accessible radius, verifying trigger conditions and activation method from user history.
3. Build Execution Version with time-stamped blocks, contingency annotations, resource references, cost/contact details, and the Day-3 reflection checkpoint with all three adjustment rules embedded at end of Day 3.
4. Distill into Family Group Chat Version by extracting only role-agnostic, time-bound, emotionally reassuring facts — remove all planner-facing metadata (e.g., 'train code G1023', 'QR link', 'budget line item'); retain only high-signal, low-cognition elements: icons, short lines, and action prompts (e.g., 'Grandma: just sit and sip → view rain on lake').
5. Output both versions consecutively, clearly labeled, with no shared headers or merged formatting.

## Triggers

- 输出执行版和家庭群简版
- 生成两个版本
- 要一个详细版和一个发群里的简版
- 做一份给管家看、一份给家人看
- 增加每周复盘步骤和调整规则
