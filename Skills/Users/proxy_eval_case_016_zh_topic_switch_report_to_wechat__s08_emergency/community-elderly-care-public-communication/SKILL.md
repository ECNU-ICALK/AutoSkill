---
id: "522e82fe-de26-437c-80bc-c0efd69249aa"
name: "community-elderly-care-public-communication"
description: "Transforms formal, policy-oriented community elderly care reports into accessible, empathetic WeChat public account articles for general families — preserving all verifiable facts (deadlines, metrics, roles, accountability) while replacing bureaucratic language with plain, conversational Mandarin grounded in real-life concerns and actionable takeaways."
version: "0.1.1"
tags:
  - "public-communication"
  - "elderly-care"
  - "family-audience"
  - "wechat-article"
  - "de-bureaucratization"
  - "fact-preserving"
triggers:
  - "改写成公众号文章，面向普通家庭"
  - "用家常话解释社区养老新变化"
  - "把政策报告变成朋友圈能转发的暖心文"
  - "转成家长能看懂的养老服务说明"
  - "写一篇给子女看的居家照护指南"
---

# community-elderly-care-public-communication

Transforms formal, policy-oriented community elderly care reports into accessible, empathetic WeChat public account articles for general families — preserving all verifiable facts (deadlines, metrics, roles, accountability) while replacing bureaucratic language with plain, conversational Mandarin grounded in real-life concerns and actionable takeaways.

## Prompt

# Goal
Rewrite a formal community elderly care optimization report into a warm, trustworthy, and practical WeChat public account article for adult children and family caregivers. The output must be audience-aligned: written in plain, conversational Mandarin; centered on 'what this means for your family'; grounded in real-life concerns (safety, dignity, daily support, peace of mind); and free of jargon — while preserving *all* original facts: departments/roles, deadlines, quantitative targets, accountability assignments, and implementation scope.

# Constraints & Style
- Language: Everyday Mandarin — no official phrasing (e.g., avoid '推进''健全''压实责任'), no passive voice, no bureaucratic nominalizations ('优化工作' → '怎么让爸妈在家更安心'); replace policy verbs with active, human-centered ones ('a social worker will visit', 'you’ll get a personalized card')
- Tone: Calm, respectful, non-alarmist — acknowledge challenges without inducing helplessness; emphasize agency, small wins, and concrete next steps; no exaggerated optimism or emotional manipulation
- Structure: Use short paragraphs, clear subheadings (no roman numerals), and line breaks for mobile readability; open with a relatable human moment (e.g., 'Last week, Aunt Li called asking how to video-call her grandson — but couldn’t find the icon'); close with 2–3 specific, low-barrier actions readers can take *this week*
- Content boundaries: Retain *all* verifiable facts — names of departments/roles (e.g., 'Street Public Service Office'), deadlines ('by end of Q3 2024'), metrics ('service matching rate ≥85%', 'fall detection accuracy ≥92%'), accountability ('funds disbursed within 15 working days', 'third-party spot checks cover ≥5% of service recipients') — embed them naturally in narrative context (e.g., 'by year-end, 9 out of 10 seniors with clear needs will receive well-matched support'); omit only internal governance markers (e.g., 'Section III', 'Annex 1', 'Draft Complete'), budget figures, legal references, and implementation timelines *not present in source*
- De-identification: Replace all proper nouns (street names, cities, institutions, programs) with generic placeholders like <LOCAL_COMMUNITY>, <CITY>, or omit entirely if not essential to meaning; preserve accountable units plainly if named in source
- Length: 800–1,200 Chinese characters — tight, scannable, value-dense

# Workflow
1. Extract all factual anchors from the source: actors (departments/roles), actions (what will be done), deadlines (when), metrics (how success is measured), and accountability (who ensures it)
2. Reframe each as a 'what changes for you' statement grounded in lived experience — e.g., 'New fall-detection devices mean fewer midnight panic calls' instead of 'Deploy millimeter-wave radar'; anchor claims in implied or anonymized vignettes ('some parents we spoke with...') rather than statistics
3. Map each anchor to a relatable household scenario (e.g., 'quarterly dynamic needs assessment' → 'a friendly chat with a community worker every 3 months to update what kind of help your parent really needs')
4. End with 2–3 concrete, zero-cost or low-effort actions — e.g., 'Ask your local community center this week: Do they offer free smartphone help?'
5. Apply final tone check: Would a tired adult child, reading on their phone during lunch break, feel seen, informed, and gently empowered?

## Triggers

- 改写成公众号文章，面向普通家庭
- 用家常话解释社区养老新变化
- 把政策报告变成朋友圈能转发的暖心文
- 转成家长能看懂的养老服务说明
- 写一篇给子女看的居家照护指南
