---
id: "8b79b5f6-803c-457c-bd93-432b835ed5d7"
name: "pet-care-handover-protocol"
description: "Generates a structured, actionable pet care handover protocol for temporary human caregivers during the owner's absence, enforcing synchronized clinical escalation rules and mirroring core care modules (feeding, walking, grooming, deworming, weight tracking) from the owner's daily plan."
version: "0.1.1"
tags:
  - "pet-care"
  - "handover"
  - "checklist"
  - "temporary-care"
  - "clinical-escalation"
  - "template"
  - "protocol"
triggers:
  - "prepare pet handover for caregiver"
  - "create dog sitter instructions"
  - "plan pet care while traveling"
  - "generate temporary pet care checklist"
  - "document pet routine for someone else"
  - "generate daily and handover dog care plans"
  - "create dual-mode pet routine"
  - "split owner vs caregiver care checklist"
  - "make parallel pet care templates"
  - "sync routine and handover protocols"
---

# pet-care-handover-protocol

Generates a structured, actionable pet care handover protocol for temporary human caregivers during the owner's absence, enforcing synchronized clinical escalation rules and mirroring core care modules (feeding, walking, grooming, deworming, weight tracking) from the owner's daily plan.

## Prompt

# Goal
Generate a clear, step-by-step pet care handover protocol for a temporary caregiver (e.g., friend, family member, or professional pet sitter) to ensure continuity of core care during the owner’s absence — strictly including: feeding schedule & portions, walking frequency/duration/route, grooming/hygiene tasks, medication or supplement administration (if any), parasite prevention timing, weight or symptom observation notes, emergency contact list, and physical交接 logistics (keys, access, supplies location). All clinical escalation rules must be embedded verbatim and enforced identically to the owner’s daily plan.

# Constraints & Style
- Output only in plain Markdown (no HTML, no code blocks, no emojis).
- Use concise, imperative language (e.g., "Give 120g kibble at 7:30 AM", "Walk for 25 min along Oak St, avoid off-leash park").
- Never invent medical details, dosages, or unconfirmed product names — if absent from input, state "[Not specified]".
- Explicitly separate sections: ▶️ Care Schedule, ▶️ Health & Monitoring, ▶️ Emergency Protocol, ▶️ Logistics & Access.
- Omit general advice (e.g., "be kind to the dog") — only include executable, time-bound, location- or item-specific instructions.
- De-identify all personal names, addresses, phone numbers, brand names (replace with <DRUG_NAME>, <LOCATION>, <CONTACT_ROLE>), and exact dates (use relative phrasing like "Day 1 of absence" or "48 hours before return").
- Embed clinical escalation rules verbatim: (a) single-day intake <60% → immediate observation; (b) two consecutive days <80% → vet within 24h; (c) <80% + vomiting/sleepiness/diarrhea → emergency within 2h; (d) weekly weight loss >3% → recheck within 48h.
- Grooming: prohibit bathing during handover period; mark as "❌ (post-return only)".
- Deworming: if due during absence, require pre-departure completion and explicit notation: "✅ Pre-trip: [Date], <DRUG_NAME>".
- Weight tracking: mandate same scale, time, and location across both plans; require photo-verified entry.
- For missing but critical items (e.g., emergency vet, key location), insert placeholder lines marked "[Owner to complete]" — never omit the field.
- Preserve all placeholders (<DOG_NAME>, <CURRENT_WEIGHT_KG>, <DRUG_NAME>) — do not populate them.

# Workflow
1. Extract confirmed care elements from user input: feeding times/amounts, walk routine, wash/groom needs, parasite prevention due date, weight tracking requirement, and any observed health notes.
2. Map each element to a fixed handover section using the four required headers.
3. For missing but critical items (e.g., emergency vet, key location), insert placeholder lines marked "[Owner to complete]" — never omit the field.
4. Output final protocol with no introduction, summary, or assistant commentary.

## Triggers

- prepare pet handover for caregiver
- create dog sitter instructions
- plan pet care while traveling
- generate temporary pet care checklist
- document pet routine for someone else
- generate daily and handover dog care plans
- create dual-mode pet routine
- split owner vs caregiver care checklist
- make parallel pet care templates
- sync routine and handover protocols
