---
id: "372deb91-250f-4e6a-a7e1-da2ace7b259d"
name: "insurance-claim-progress-sync-schedule"
description: "A reusable skill for scheduling and executing periodic, structured progress updates to an insurance company during a property claim, enforced at fixed intervals."
version: "0.1.0"
tags:
  - "insurance"
  - "claim-management"
  - "communication-scheduling"
  - "compliance"
triggers:
  - "sync claim progress with insurer"
  - "update insurer every 3 business days"
  - "schedule periodic claim status updates"
  - "maintain insurer communication cadence"
  - "track claim timeline with insurer"
---

# insurance-claim-progress-sync-schedule

A reusable skill for scheduling and executing periodic, structured progress updates to an insurance company during a property claim, enforced at fixed intervals.

## Prompt

# Goal
Generate a concise, professional, and insurer-appropriate progress update message to be sent to the insurance company every 3 business days throughout the claim lifecycle.

# Constraints & Style
- Must be sent exactly every 3 business days (exclude weekends and public holidays); do not drift or approximate.
- Message must include: (1) Claim reference number (if known), (2) Brief status summary (e.g., 'awaiting surveyor appointment', 'repair quote submitted'), (3) Clear indication of next expected action or pending item, (4) Zero emotional language, speculation, or informal phrasing.
- Never include unsolicited documentation, attachments, or new evidence — this is strictly a status sync, not a submission.
- If no material change occurred, state 'No material update; claim remains in [current stage]' — do not omit the sync.
- Do not invent or assume internal insurer processes (e.g., 'your underwriting team is reviewing'). Stick only to verifiable external status.

# Workflow
1. On Day 0: Record claim initiation date and first sync due date (3 business days later).
2. On each sync date: Retrieve latest verified status (e.g., from call log, email, portal), compose message per constraints.
3. Send via insurer’s preferred channel (email/portal message) and log timestamp + content.
4. Auto-calculate and record next sync date before closing.

## Triggers

- sync claim progress with insurer
- update insurer every 3 business days
- schedule periodic claim status updates
- maintain insurer communication cadence
- track claim timeline with insurer
