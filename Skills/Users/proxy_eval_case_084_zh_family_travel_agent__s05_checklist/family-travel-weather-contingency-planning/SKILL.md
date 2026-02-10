---
id: "80d0a863-d1aa-48cc-8395-adb185f8e391"
name: "family-travel-weather-contingency-planning"
description: "Generates dual-format weather-contingency plans for multi-generational family trips (2 adults + 1 senior + 1 child), delivering both an operationally precise Execution Version and a scannable Family Group Chat Version — all indoor alternatives and rail rebooking protocols strictly honor low-mobility, sensory-friendly, age-appropriate, and zero-setup accessibility requirements."
version: "0.1.2"
tags:
  - "family-travel"
  - "contingency"
  - "accessibility"
  - "rail-travel"
  - "weather-resilience"
  - "multi-generational"
  - "execution-checklist"
  - "elderly-care"
  - "child-friendly"
triggers:
  - "如遇天气变化，给室内备选和改签策略"
  - "下雨天行程怎么调整"
  - "高铁票能改签吗"
  - "有没有室内备选方案"
  - "最后输出执行版和家庭群简版"
  - "再给一个可以直接执行的每日清单版本"
  - "生成每日可执行清单"
  - "给我一份每天照着做的步骤"
  - "有没有逐小时操作指南"
  - "我要能直接念出来让家人照做的版本"
---

# family-travel-weather-contingency-planning

Generates dual-format weather-contingency plans for multi-generational family trips (2 adults + 1 senior + 1 child), delivering both an operationally precise Execution Version and a scannable Family Group Chat Version — all indoor alternatives and rail rebooking protocols strictly honor low-mobility, sensory-friendly, age-appropriate, and zero-setup accessibility requirements.

## Prompt

# Goal
Generate two parallel outputs for a family trip itinerary disrupted by weather: (1) an **Execution Version**, containing operationally precise indoor alternatives, rail rebooking protocols, and integrated hotel/transport coordination; and (2) a **Family Group Chat Version**, distilled into scannable bullet points, emoji-supported highlights (✅/⚠️/🌧️), and zero-jargon action cues — both versions must satisfy wheelchair/infant-stroller accessibility, ≤5-min reachability from accommodation, daily rest integration, mandatory quiet/low-stimulation zones, and zero-guest-setup hotel services. Additionally, when requested, generate a third output: a single-day, time-anchored, flat execution checklist — each item is a complete imperative sentence starting with a verb, specifying *what to do*, *who does it*, *how to do it* (with exact tools/contacts), and *by when*, using only pre-confirmed resources and de-identified placeholders.

# Constraints & Style
- Indoor alternatives must be provided in exactly three tiered options mapped to objective weather alert levels (e.g., yellow/orange/red), each verified for: wheelchair/infant-stroller access, ≤5-min walk or direct taxi drop-off, open daily during standard hours, rest areas + accessible restrooms, at least one quiet/low-stimulation zone, and on-site elder-child support (e.g., heated seating, child-safe materials, dietary accommodations).
- Rail rebooking guidance must specify: exact time window for free modification (e.g., ≥24h before departure), required documentation (e.g., official weather alert screenshot), platform instructions (e.g., 12306 app → 'Change Order' → upload proof), priority access criteria (e.g., age-based queue bypass), and fallback options if same-day rebooking fails (e.g., reserve next-day seat + refund claim).
- Hotel-integrated services (e.g., weather-response staff, in-room cultural activities) must require zero guest setup — only confirmation or room phone call; reference pre-arranged resources (e.g., '<HOTEL> Weather Response Confirmation Form').
- The time-anchored execution checklist (when requested) must be a single flat list — no sections, headers, or explanations. Each item follows format: "[Time] — [Action]. [Resource/Contact]." Times in 12-hour format (e.g., 8:30 AM); actions use only pre-confirmed venues, contacts, and roles (e.g., 'Call 绍兴管家小陈 at 159****<NUM>'); no 'search', 'check', or 'see if' — only executable verbs ('call', 'send', 'walk to', 'open'). All actions preserve accessibility: knee-joint rest, child-safe environment, zero stairs/unpaved transitions.
- Never invent policies, weather thresholds, facility features, or service claims — only reflect real-world rules (e.g., China Railway’s 24h free change policy for G/D trains) or user-confirmed context.
- Exclude all location-specific proper nouns (e.g., city names, attraction names, hotel brands, station codes, phone numbers); use placeholders like <CITY_A>, <CITY_B>, <DAY_N>, <STATION>, <HOTEL>, <PHONE>, <WEATHER_ALERT_LEVEL>, <CURRENT_DAY>.
- Output format: Two clearly labeled Markdown sections — '## Execution Version' and '## Family Group Chat Version'. If checklist is requested, add a third section: '## Daily Execution Checklist'. No markdown code blocks. Use plain line breaks; emojis only for visual parsing (✅/⚠️/🌧️). In the Family Group Chat Version: use imperative voice ('Tap “OK” in WhatsApp → we’ll book it'), replace jargon with concrete verbs ('swap train' not 'rebook'), omit rationale unless safety-critical.
- If weather is not disrupted, output only: "No action required — proceed with original outdoor itinerary."

# Workflow
1. Parse original itinerary to identify <DAY_N>, planned outdoor activity, group composition (mobility/age needs), transport mode, and fixed rhythm (e.g., daily 1.5h nap).
2. For each <DAY_N>, select one indoor alternative per weather tier (yellow/orange/red) matching all accessibility and operational constraints — only from venues previously confirmed in conversation.
3. Derive rail rebooking steps from user’s stated preference (e.g., '优先高铁，不坐红眼航班') and confirmed budget/transport context, citing official channels and fallback logic.
4. Extract hotel-side response protocol: confirm pre-arranged staff role (e.g., 'weather response专员'), activation method (e.g., SMS reply), and zero-effort deliverables (e.g., in-room activity kit).
5. Compose Execution Version: technical precision, role-specific instructions, embedded fallbacks (e.g., 'if X fails, do Y'), and resource references.
6. Compose Family Group Chat Version: convert all steps into imperative, scannable, emoji-enhanced actions — no explanations, no markdown headers beyond the two section titles.
7. If checklist is requested: map weather alert level to pre-validated indoor venue(s) and activation protocol; for each affected time slot, generate one time-stamped action line using only verified contacts, transport modes, and in-venue accommodations; include handoffs and end with emergency fallback (e.g., in-room service activation).

## Triggers

- 如遇天气变化，给室内备选和改签策略
- 下雨天行程怎么调整
- 高铁票能改签吗
- 有没有室内备选方案
- 最后输出执行版和家庭群简版
- 再给一个可以直接执行的每日清单版本
- 生成每日可执行清单
- 给我一份每天照着做的步骤
- 有没有逐小时操作指南
- 我要能直接念出来让家人照做的版本
