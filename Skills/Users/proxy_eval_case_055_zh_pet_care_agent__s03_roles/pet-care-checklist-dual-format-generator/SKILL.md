---
id: "a8c42071-d0f1-40f8-999f-8dba233293ff"
name: "pet-care-checklist-dual-format-generator"
description: "Transforms comprehensive pet care plans into two specialized checklist formats: a concise daily operational version for owner use and a detailed handover version for temporary caregiving arrangements, while preserving critical escalation protocols."
version: "0.1.0"
tags:
  - "checklist"
  - "care plan"
  - "handover"
  - "dual-format"
  - "pet care"
triggers:
  - "generate daily pet care checklist"
  - "create pet sitter handover checklist"
  - "convert comprehensive care plan to dual formats"
---

# pet-care-checklist-dual-format-generator

Transforms comprehensive pet care plans into two specialized checklist formats: a concise daily operational version for owner use and a detailed handover version for temporary caregiving arrangements, while preserving critical escalation protocols.

## Prompt

# Goal
Generate two distinct checklist formats from a comprehensive pet care plan: (1) a compact daily use version for the owner, and (2) a detailed handover version for temporary caregivers, ensuring both maintain critical health monitoring and escalation rules.

# Constraints & Style
- Daily checklist: Minimalist, action-oriented, omit explanatory text, focus on actionable tasks with clear frequency indicators
- Handover checklist: Comprehensive, documentation-focused, include all contextual information, escalation procedures, and contact details
- Both versions must contain: feeding schedules, exercise requirements, health monitoring protocols, and escalation triggers for appetite loss
- Maintain consistent terminology across both formats
- Use bullet points and clear section headers for scannability
- Include quick-reference escalation tables for appetite loss (24-hour vs 48-hour thresholds)
- Omit specific pet details, medical conditions, and time-sensitive references (e.g., "10-day trip")

# Workflow
1. Extract core daily operational tasks from comprehensive plan
2. Identify contextual and emergency information for handover version
3. Map escalation protocols to both formats with appropriate detail level
4. Format daily version as quick-reference checklist with action verbs
5. Format handover version as complete documentation with all necessary details
6. Validate both versions contain equivalent critical information

## Triggers

- generate daily pet care checklist
- create pet sitter handover checklist
- convert comprehensive care plan to dual formats
