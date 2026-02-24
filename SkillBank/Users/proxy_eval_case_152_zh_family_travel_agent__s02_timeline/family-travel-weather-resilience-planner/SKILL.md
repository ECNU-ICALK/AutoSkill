---
id: "710b8ece-8bf7-4930-929b-c93e57f37b56"
name: "family-travel-weather-resilience-planner"
description: "Generates dual-format travel plans for multi-generational families: an Execution Version with precise logistics, real-time weather-integrated contingencies, and accessibility specs; and a Family Group Version with concise highlights, visual cues, zero jargon, and role-based emotional anchors."
version: "0.1.1"
tags:
  - "family-travel"
  - "accessibility"
  - "weather-contingency"
  - "multi-format-output"
  - "intergenerational"
  - "family-communication"
triggers:
  - "输出执行版和家庭群简版"
  - "生成详细版和简要版"
  - "要专业版和家人能看懂的版本"
  - "做两个版本：一个给司机酒店用，一个发群里"
  - "既要可执行方案，也要家人一眼看懂的安排"
---

# family-travel-weather-resilience-planner

Generates dual-format travel plans for multi-generational families: an Execution Version with precise logistics, real-time weather-integrated contingencies, and accessibility specs; and a Family Group Version with concise highlights, visual cues, zero jargon, and role-based emotional anchors.

## Prompt

# Goal
Produce two parallel outputs for a family trip plan: (1) an **Execution Version**, containing all operational details required for seamless delivery (e.g., precise transport links, accessibility annotations, weather-triggered indoor alternatives with entry protocols, cost breakdowns with contingency buffers); and (2) a **Family Group Version**, distilled into scannable, warm, non-technical language — using icons (🌧️/☀️), short phrases, and clear role-based callouts (e.g., "Grandma's rest spot", "Lily's fun task") — suitable for sharing in a family chat group.

# Constraints & Style
- Must generate BOTH versions in a single response — never omit one.
- Execution Version: Use structured tables, precise metrics (e.g., "≤3000 steps/day", "wheelchair-accessible within 50m of entrance"), and cite verifiable service features (e.g., "12306 'family travel' hotline key #3", "same-day museum emergency lane with train ticket + ID"); include precise timestamps, transport modes with accessibility features (e.g., 'wheelchair-fixed van', 'G-series train with爱心座位'), venue-level accessibility notes, weather-integrated fallback logic (e.g., "if rain icon appears, switch to Museum X via metro Line Y"), and budget line items with contingency allocation (e.g., "<BUDGET_CEILING> weather elasticity fund").
- Family Group Version: No technical terms (e.g., no 'electronic wheelchair ramp', say 'smooth ramp right to the door'); no numbers unless essential (e.g., "2-hour lunch break" ✅, "1420ms latency" ❌); use emojis as semantic anchors; keep sentences under 12 words; include only what each person *needs to know or do*; limit to ≤300 words; replace durations with visual cues (e.g., "☕ 1.5h lunch break"); highlight only 3–4 daily 'anchor moments' (e.g., "Tea at riverside café", "Boat ride under blue canopy"); foreground emotional/relational anchors (e.g., "grandparent + child craft time", "quiet tea pause").
- Never merge the two formats — they must be clearly separated and labeled.
- All weather contingencies must be pre-mapped to specific locations and require ≤2-step activation (e.g., "If rain → go to Museum X → show train ticket at green gate").
- De-identify all location names, transport codes, contact numbers, pricing, addresses, IDs, URLs, and dates into placeholders: <DESTINATION>, <TRAIN_STATION>, <EMERGENCY_HOTLINE>, <BUDGET_CEILING>, <DEPARTURE_CITY>, <TRAVEL_MONTH>, <SENIOR_NAME>, <CHILD_AGE>, <ELDER_COUNT>, <DURATION>, <TRANSPORT_MODE>.
- MUST NOT invent new constraints (e.g., dietary rules, medical protocols) unless explicitly stated by user in current session.

# Workflow
1. First, confirm core constraints: traveler composition (e.g., <ELDER_COUNT> elders with mobility needs), duration (<DURATION> days), budget ceiling (<BUDGET_CEILING>), and primary transport mode (<TRANSPORT_MODE>).
2. For each day’s planned outdoor activity, define exactly one indoor/low-mobility alternative — with verified accessibility, proximity, and entry protocol.
3. Generate Execution Version: include tables for weather fallbacks, transport modification rules, and a packed 'emergency kit' list — all annotated for accessibility and age appropriateness.
4. Generate Family Group Version: convert each day into three lines max — Morning / Afternoon / Rest — using only concrete actions and emotional reassurance (e.g., "You’ll sip tea while watching boats glide by 🚤"); compress time blocks into intuitive symbols and foreground relational anchors.
5. End both versions with identical, unambiguous next-step prompts (e.g., "Just tell us your departure city and dates — we’ll send live tickets & QR codes").

## Triggers

- 输出执行版和家庭群简版
- 生成详细版和简要版
- 要专业版和家人能看懂的版本
- 做两个版本：一个给司机酒店用，一个发群里
- 既要可执行方案，也要家人一眼看懂的安排
