---
id: "610b0cc8-0cd3-4da5-81f7-fadf8b500fba"
name: "multi-generational-weather-resilient-travel-planning"
description: "Generates fully weather-adaptive travel plans for multi-generational families, embedding zero-step indoor fallbacks, pre-verified transport rebooking protocols, accessibility-guaranteed continuity, and a role-specific handover protocol — all aligned to knee-friendly, low-step, high-rest constraints."
version: "0.1.2"
tags:
  - "family-travel"
  - "accessibility"
  - "weather-resilience"
  - "multi-generational"
  - "contingency-planning"
  - "handoff-protocol"
triggers:
  - "如遇天气变化，给室内备选和改签策略"
  - "下雨天行程怎么调整"
  - "高温预警时有什么室内方案"
  - "高铁票能免费改签吗"
  - "天气不好怎么保障老人孩子舒适"
  - "明确家庭成员/参与者分工和交接节点"
  - "谁负责通知酒店改期"
  - "下雨时谁带老人去室内点"
  - "孩子走散了谁第一时间联系"
  - "高铁晚点后谁对接接驳车"
---

# multi-generational-weather-resilient-travel-planning

Generates fully weather-adaptive travel plans for multi-generational families, embedding zero-step indoor fallbacks, pre-verified transport rebooking protocols, accessibility-guaranteed continuity, and a role-specific handover protocol — all aligned to knee-friendly, low-step, high-rest constraints.

## Prompt

# Goal
Generate a resilient, executable travel plan for a multi-generational family trip that maintains full accessibility (zero stairs, low walking load, mandatory midday rest) regardless of weather, by embedding three layers of response: (1) graded indoor alternatives matching the same physical & cognitive accessibility standards as the outdoor plan; (2) frictionless, cost-controlled transport rebooking rules (free 高铁改签, delay compensation, automatic rescheduling); and (3) on-demand hotel-based care services (remote telehealth, in-room activities, nutrition-adjusted meals); plus (4) a precise, de-identified handover protocol defining who does what—and when—during weather-triggered adjustments.

# Constraints & Style
- Must enforce strict knee-accessibility continuity: every indoor alternative must have flat-floor access, abundant seating, climate control, no standing >20 min, and walking ≤2.5 km/day.
- Must include only pre-verified, partner-confirmed options: venues with signed accessibility certifications, hotels with documented knee-support amenities (e.g., bed assist rails, thermal foot warmers), and transport providers trained in elder/child mobility assistance.
- Must avoid generic suggestions — instead specify exact venue names, verified features (e.g., 'Zhejiang Art Museum: Level 0 entry, 12+ quiet rest pods, tactile floor maps'), and real-time triggers (e.g., 'if 12306 shows >30min delay, auto-switch to direct hotel drop-off').
- Must output two parallel versions: (A) an *Execution Version* (detailed, time-stamped, role-assigned, with contact links and fallback logic), and (B) a *Family Group Summary* (concise, emoji-annotated, decision-light, optimized for quick scanning in WeChat group chat).
- Must exclude all one-off details: specific dates, departure cities, child ages, or booking IDs — retain only reusable policy logic and structural patterns.
- Must not invent unconfirmed capabilities; only encode actions operationally guaranteed via partner agreements or platform features (e.g., 12306’s weather-based refund API, hotel-signed 'extreme weather stay extension' clause).
- Must exclude all outdoor-only, stairs-dependent, or non-climate-controlled options.
- Indoor alternatives must be within 15 minutes’ accessible transit (e.g., low-floor shuttle, elevator-equipped walk) from the original hotel or activity hub.
- Rebooking instructions must specify exact platforms: 12306 app steps (with screenshot descriptors), station service counter codes (e.g., '爱心通道 A3'), and pre-approved contact numbers for priority assistance.
- Handover protocol must define functionally labeled roles (e.g., 'Primary Coordinator', 'On-Site Caregiver', 'Child Supervisor'), their atomic, verifiable tasks per weather tier, and unambiguous handoff nodes — each including trigger condition, required action, deadline (e.g., 'within 5 minutes'), delivery channel (e.g., 'via WhatsApp group'), and success signal (e.g., 'reply with ✅').
- Roles must be duty-based, not person-based; use placeholders <WEATHER_TIER>, <PRIMARY_COORDINATOR>, <ON_SITE_CAREGIVER>, <CHILD_SUPERVISOR>, <HANDOFF_CHANNEL> — never case-specific names or entities.
- Output format: four clear sections — 'Indoor Backup Activities (by Day)', 'Real-Time Rebooking Protocol', 'Handover Protocol Table', and 'Family Group Summary' — using plain language, no markdown tables or nested lists.
- Never invent facility names or services not confirmed in official 2024 accessibility reports or operator announcements.

# Workflow
1. Parse user’s core accessibility constraint (e.g., 'knee impairment → max 3000 steps/day + daily 12:30–14:30 rest').
2. For each day’s original outdoor itinerary, generate three weather-tiered indoor alternatives — each satisfying identical accessibility invariants.
3. Embed transport contingency: map each weather/latency condition to a pre-agreed action (e.g., '≥30min train delay → activate free private transfer to hotel, no approval needed').
4. Encode hotel-side service escalation: define automatic triggers for in-room care (e.g., 'red alert → dispatch licensed therapist within 90 min').
5. Define handover protocol: assign roles, responsibilities per weather tier, and handoff nodes with trigger, action, deadline, channel, and confirmation.
6. Output both versions:
   - Execution Version: tabular hourly schedule with columns [Time, Activity, Accessibility Proof, Weather Trigger, Owner, Contact]; includes appendices (partner verification logs, policy clauses, QR-linked resources) and the Handover Protocol Table.
   - Family Group Summary: bullet-point digest using ✅/⚠️/☔ icons; omits times, contacts, and technical terms; uses phrases like 'No stairs. Nap time locked. Rain? We move indoors — same comfort.'

## Triggers

- 如遇天气变化，给室内备选和改签策略
- 下雨天行程怎么调整
- 高温预警时有什么室内方案
- 高铁票能免费改签吗
- 天气不好怎么保障老人孩子舒适
- 明确家庭成员/参与者分工和交接节点
- 谁负责通知酒店改期
- 下雨时谁带老人去室内点
- 孩子走散了谁第一时间联系
- 高铁晚点后谁对接接驳车
