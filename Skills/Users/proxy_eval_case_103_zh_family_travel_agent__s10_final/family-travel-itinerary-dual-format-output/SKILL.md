---
id: "d7df6349-ff70-444c-b568-c38e2b85800c"
name: "family-travel-itinerary-dual-format-output"
description: "Generates travel itineraries in two parallel, strictly synchronized versions: a detailed 'Execution Version' for planners (with step-by-step logistics, accessibility annotations, and weather-triggered fallbacks) and an abridged 'Family Group Chat Version' for shared clarity (concise, action-oriented, no jargon) — both enforcing core user constraints including low-step terrain, zero stairs, fixed midday rest,高铁-only transport, budget cap, and knee-friendly infrastructure."
version: "0.1.1"
tags:
  - "travel-planning"
  - "accessibility"
  - "multi-format-output"
  - "family-communication"
  - "contingency-planning"
  - "constraint-enforcement"
triggers:
  - "输出执行版和家庭群简版"
  - "生成两个版本"
  - "要一个详细版和一个发群里的简版"
  - "做一份可执行的+一份家人能看懂的"
  - "最终版要求：简洁、可执行、检查点不遗漏"
---

# family-travel-itinerary-dual-format-output

Generates travel itineraries in two parallel, strictly synchronized versions: a detailed 'Execution Version' for planners (with step-by-step logistics, accessibility annotations, and weather-triggered fallbacks) and an abridged 'Family Group Chat Version' for shared clarity (concise, action-oriented, no jargon) — both enforcing core user constraints including low-step terrain, zero stairs, fixed midday rest,高铁-only transport, budget cap, and knee-friendly infrastructure.

## Prompt

# Goal
Produce two synchronized itinerary outputs for a family trip with mobility-sensitive members: (1) a comprehensive Execution Version for detailed planning and operational use, and (2) a concise Family Group Chat Version optimized for quick scanning, sharing, and real-time coordination in messaging apps.

# Constraints & Style
- Both versions must reflect the *same* core constraints: daily walking ≤3000 steps, zero stairs/unpaved/uneven surfaces, guaranteed 1.5–2h midday rest,高铁-only daytime transit (no red-eye trains), total budget ≤¥15,000 for 4 people × 6 days, and weather-resilient indoor alternatives with verifiable accessibility details.
- Execution Version: structured with timestamps, transport codes (e.g., G1023), venue accessibility annotations (e.g., "wheelchair ramp at East Gate", "rest benches every 25m"), exact step-count estimates per day, contingency triggers (e.g., "if rain >3mm/hr → switch to浙博之江馆"), and itemized budget breakdown; include logistical assets: hotel room configuration notes, pharmacy proximity, emergency contact cards, and knee-support resource availability (e.g., "hotel lends heated knee wraps").
- Family Group Chat Version: ultra-condensed (≤120 words total), plain-language, emoji-supported, mobile-optimized — omit technical codes, internal logic, and marketing language; highlight only *what*, *when*, *where*, and *why it’s easy*: e.g., "☀️ 10:00–12:00 West Lake boat ride (no walking!) → 🛏️ 13:00–15:00 hotel nap + tea → 🌧️ Rain? → 🏛️ Zhejiang Museum (wheelchair OK, soft seats every 20m)"; state constraints plainly: "All days under 3k steps", "No stairs — all spots have ramps or rides", "Rest time locked: 13:00–15:00 daily", "All trips by comfortable daytime高铁 — no overnight trains", "Total: ¥14,680 — under budget!"
- No proper nouns tied to specific trips (e.g., avoid 'Grandma Li', 'Hotel A'); use placeholders like <HOTEL_NAME>, <DESTINATION>, <DEPARTURE_CITY>, <CHILD_AGE>.
- Never invent new constraints — only encode those user-confirmed: knee sensitivity, fixed rest window, indoor fallbacks,高铁-only transit with time bounds, and budget ceiling.

# Workflow
1. Parse confirmed constraints: mobility limits, rest requirement, weather contingency, transport rules, and budget cap.
2. Generate Execution Version first — fully annotated, precise, operationally actionable, with verifiable detail (no unpopulated placeholders for step counts, rest locations, train IDs, or budget line items).
3. Derive Family Group Chat Version *from* the Execution Version — distill, simplify, localize time/place cues, add supportive emojis, remove all implementation metadata (e.g., no 'step count: 2,840').
4. Validate strict alignment: same daily structure, same fallbacks, same timing logic, same budget total, same transport mode — no divergence in substance.

## Triggers

- 输出执行版和家庭群简版
- 生成两个版本
- 要一个详细版和一个发群里的简版
- 做一份可执行的+一份家人能看懂的
- 最终版要求：简洁、可执行、检查点不遗漏
