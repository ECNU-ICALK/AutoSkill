---
id: "43b04e39-eeb6-4de6-89cc-cdaed1829325"
name: "cross-city-moving-role-allocation"
description: "Generates a clear, de-identified, plain-text three-role task allocation plan for cross-city relocation — assigning time-bound, non-overlapping responsibilities to the user (external coordination), immediate family (on-site execution), and parents (sensory verification and emotional grounding) — optimized for reliability under disruption and zero formatting overhead."
version: "0.1.1"
tags:
  - "relocation"
  - "task-allocation"
  - "family-coordination"
  - "role-based-planning"
  - "crisis-response"
  - "plain-text"
triggers:
  - "给我家人父母三套分工清单"
  - "分配搬家任务给三类人"
  - "角色分工搬家计划"
  - "谁负责什么搬家任务"
  - "家庭成员搬家职责划分"
---

# cross-city-moving-role-allocation

Generates a clear, de-identified, plain-text three-role task allocation plan for cross-city relocation — assigning time-bound, non-overlapping responsibilities to the user (external coordination), immediate family (on-site execution), and parents (sensory verification and emotional grounding) — optimized for reliability under disruption and zero formatting overhead.

## Prompt

# Goal
Generate a reusable, role-based task allocation framework for cross-city relocation, assigning responsibilities across three distinct stakeholder roles: (1) the user (external coordination only), (2) immediate family (on-site internal execution and setup), and (3) parents (environmental verification and calm anchoring). Output must be fully de-identified — no city names, proper nouns, dates, contact details, addresses, budget figures, vendor names, app names, URLs, or case-specific logistics.

# Constraints & Style
- Output must be plain text only: NO tables, NO markdown headers, NO bullet symbols (•/▪️), NO emojis, NO bold/italic formatting.
- Use only line breaks and short imperative sentences (max 12 words per line).
- Each role section starts with exactly: "[Role]:" (e.g., "User:") followed by colon and newline.
- All tasks are phrased as direct instructions: "Do X", "Send Y", "Check Z".
- Tasks must reflect realistic capability boundaries: parents’ tasks rely only on sensory input (sight, sound, smell, touch) and lived experience — no digital tools or reading; family tasks require no lifting >10kg and no access to external systems; user tasks involve only one external contact per action and never include negotiation or explanation.
- All tasks must be executable in <5 minutes each and require no technical setup.
- Enforce a 'stability-over-speed' policy: prioritize verifiability, low cognitive load, and minimal dependencies.
- Include exactly one universal coordination rule at the end: "All updates go to one shared group chat named 'Relocation Command'."
- Output must be self-contained: no placeholders, no instructions to replace values, no explanations or disclaimers.
- No assumptions about housing type, pet ownership, or special needs — keep universally applicable.
- Use plain, imperative language (e.g., "Verify contract terms", not "You should verify...").
- All content must be abstracted from real-world relocation workflows — no invented steps; only those evidenced in user-confirmed multi-role coordination needs.

## Triggers

- 给我家人父母三套分工清单
- 分配搬家任务给三类人
- 角色分工搬家计划
- 谁负责什么搬家任务
- 家庭成员搬家职责划分
