---
id: "796f7a1e-4bab-49af-affd-ef5f8fe988ad"
name: "dog-care-plan-dual-version-generator"
description: "Generates two parallel, context-aligned care checklists — one for daily self-care and one for temporary third-party care — both derived from a shared core schedule but with role-specific constraints, handover safeguards, and escalation logic."
version: "0.1.0"
tags:
  - "pet-care"
  - "checklist-generation"
  - "delegation-safety"
  - "clinical-escalation"
  - "care-plan-versioning"
triggers:
  - "give me daily and caregiver versions"
  - "split into owner and sitter lists"
  - "two checklists: one for me, one for pet sitter"
  - "make self-use and handoff versions"
---

# dog-care-plan-dual-version-generator

Generates two parallel, context-aligned care checklists — one for daily self-care and one for temporary third-party care — both derived from a shared core schedule but with role-specific constraints, handover safeguards, and escalation logic.

## Prompt

# Goal
Generate two synchronized, printable care checklists from a single source plan: (1) a **Daily Self-Care Version**, optimized for owner consistency and health tracking; and (2) a **Temporary Caregiver Version**, stripped of non-essential tasks, pre-filled with critical instructions, and hardened against common delegation risks (e.g., unauthorized grooming, inconsistent cues, delayed escalation).

# Constraints & Style
• Both versions must share identical time-bound anchors (e.g., 'Monday 7:00 AM feeding') and reference the same underlying weekly rhythm.
• The Daily Version includes: full weight logging, preventive hygiene (e.g., weekly ear cleaning), training progression, and integrated clinical escalation rules (e.g., appetite decline thresholds).
• The Caregiver Version MUST: 
  - Remove all non-urgent, skill-dependent, or preference-based tasks (e.g., brushing, training new commands, bathing, nail trims);
  - Pre-specify *exact* food amounts, times, and medications — no ranges or 'as needed' language;
  - Embed explicit 'DO NOT' directives (e.g., 'DO NOT bathe', 'DO NOT introduce new treats', 'DO NOT change walking route');
  - Include a mandatory daily reporting template (structured text fields only: meal intake ✅/❌, stool appearance, abnormal behavior);
  - Surface only the *minimum viable escalation path*: e.g., 'If no eating for >24h → call [vet name] at [number] → say "appetite alert level 2"'.
• All medical thresholds (e.g., '48h refusal = urgent vet') must be copied verbatim from the user’s validated clinical escalation protocol — no reinterpretation.
• Output format: Two cleanly separated Markdown tables (no merged cells), each with header row and weekday rows. No narrative explanations unless requested separately.

# Workflow
1. Extract the canonical weekly schedule (feeding, walking, health checks) from the user’s base plan.
2. For the Daily Version: retain all modules, preserve tracking fields (weight, stool notes, behavior flags), and embed escalation rules inline where relevant (e.g., in 'Feeding' row: '⚠ If <30% intake ×2 meals → trigger Level 2').
3. For the Caregiver Version:
   a. Filter out any task requiring judgment, habituation, or long-term relationship (e.g., 'bonding play', 'training review', 'coat condition assessment');
   b. Replace conditional language ('if X, then Y') with binary action statements ('Do X. Do not do Y.');
   c. Inject the user’s exact clinical escalation triggers and response steps at the top as a pinned banner.
   d. Append the daily reporting template as a fixed footer.

## Triggers

- give me daily and caregiver versions
- split into owner and sitter lists
- two checklists: one for me, one for pet sitter
- make self-use and handoff versions
