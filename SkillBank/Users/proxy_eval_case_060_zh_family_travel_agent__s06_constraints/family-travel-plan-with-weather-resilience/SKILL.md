---
id: "b08fb232-d550-41ec-973c-c152f33f6fb7"
name: "family-travel-plan-with-weather-resilience"
description: "Generates a dual-format, weather-resilient 6-day high-speed rail family travel plan for 2 adults + 1 elderly + 1 child, enforcing low physical load, mandatory midday rest, accessibility, and real-world contingency protocols — with fully de-identified, copy-paste-safe execution and family-group versions."
version: "0.1.1"
tags:
  - "family-travel"
  - "accessibility"
  - "contingency-planning"
  - "multi-output"
  - "low-mobility"
  - "weather-resilience"
triggers:
  - "生成带天气弹性的家庭高铁行程"
  - "输出执行版和家庭群简版"
  - "老人孩子同行的旅行计划"
  - "家庭出游需应急改签和室内备选"
  - "不用表格，简洁清晰可复制"
---

# family-travel-plan-with-weather-resilience

Generates a dual-format, weather-resilient 6-day high-speed rail family travel plan for 2 adults + 1 elderly + 1 child, enforcing low physical load, mandatory midday rest, accessibility, and real-world contingency protocols — with fully de-identified, copy-paste-safe execution and family-group versions.

## Prompt

# Goal
Generate a dual-format, weather-resilient 6-day high-speed rail family travel plan for 4 people (2 adults + 1 elderly + 1 child), with strict adherence to low physical load, mandatory midday rest, and budget ≤¥15,000. Output two versions: (1) a full **Execution Version** (detailed, operational, print-ready, copy-paste-safe), and (2) a concise **Family Group Chat Version** (scannable, emoji-light, action-focused, no jargon, zero-fluff).

# Constraints & Style
- Must enforce: daily walking ≤3000 steps (verified route map), 13:00–15:00 non-negotiable hotel rest block, elevator-accessible/no-stairs accommodations, G-train preference with contiguous seating (elderly near aisle, child near window), and total cost capped at ¥14,800 ±¥200.
- Weather/health resilience is not optional: embed three pre-validated contingency modes — ‘Indoor Essence’ (rain/storm), ‘Cool-Time Plan’ (≥35°C), and ‘Pause Button’ (acute discomfort) — each with concrete, vendor-backed actions (e.g., same-day museum swap, clinic tele-triage, 12306 silver-channel rebooking).
- Execution Version must include: time-anchored daily schedule (with buffer minutes), exact train numbers/times, room feature checklist (L-shaped扶手, anti-slip mat, emergency button), indoor backup venue list (with walk distance <500m + accessibility rating), printable emergency card (hospital names, pharmacy addresses, 1-click taxi presets), and QR-ready resource links as plain URLs.
- Family Group Chat Version must be ≤12 lines, use only ✅/⚠️/🌧️/🌡️/💤/☀️/🌙 icons for status, omit technical terms (e.g., say ‘free same-day museum switch’ not ‘indoor essence mode’), highlight only who does what and when, and contain 3–4 critical emoji-tagged highlights per day (e.g., ❗No stairs｜❗Free stroller rental).
- All output must be table-free, markdown-free, and copy-paste safe: use only line breaks, flat bullet points (•), and minimal emoji signposts (❗☀️💤🌧️📱✨); no colons in headers, no indented sub-bullets, no asterisk emphasis, no code blocks or horizontal rules.
- Never invent destinations, vendors, or logistics; all indoor backups and medical partners must be real, geolocated within 3km of planned hotels, and verified for wheelchair access / stroller rental / pediatric service — but remain abstracted via placeholders (<DEPARTURE_CITY>, <DESTINATION_1>, <ELDERLY_MOBILITY_PROFILE>, <CHILD_AGE>).
- Prioritize clarity over completeness: deliver only actionable items — omit explanations, rationales, or meta-commentary.

# Workflow
1. Confirm departure city (<DEPARTURE_CITY>) to scope feasible high-speed rail destination cluster.
2. For each day, construct primary outdoor itinerary meeting step cap and rest window.
3. For each primary activity, pre-map one 1:1 indoor alternative (same city, ≤500m walk from hotel, ≥4.7 Google rating, verified accessibility).
4. Apply weather/health triggers to generate three parallel response protocols with executable steps (no generic advice).
5. Compile Execution Version (structured, dense, reference-ready) and Family Group Chat Version (modular, role-tagged, zero-fluff) in parallel.
6. Validate budget line items against real-time fare/hotel APIs (simulate: G-train tickets ×4, 5-night family room, 6× breakfast/dinner, 3× indoor activity fees, 2× medical concierge credits).
7. End with single-line readiness cue: "✅ Ready to deploy — just confirm <DEPARTURE_CITY>."

## Triggers

- 生成带天气弹性的家庭高铁行程
- 输出执行版和家庭群简版
- 老人孩子同行的旅行计划
- 家庭出游需应急改签和室内备选
- 不用表格，简洁清晰可复制
