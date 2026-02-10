---
id: "6e35e3ca-6ffd-4c17-b423-6d6cf7f53516"
name: "structured-insurance-claim-progress-sync"
description: "A reusable protocol for systematically updating insurers on household property insurance claim progress at fixed intervals, ensuring accountability and auditability."
version: "0.1.0"
tags:
  - "insurance"
  - "claim-management"
  - "communication-routine"
  - "compliance"
  - "time-bound"
triggers:
  - "同步理赔进度"
  - "每三天更新保险公司"
  - "定期向保险公司汇报进展"
  - "理赔过程中的阶段性反馈"
  - "保险理赔进度通报"
---

# structured-insurance-claim-progress-sync

A reusable protocol for systematically updating insurers on household property insurance claim progress at fixed intervals, ensuring accountability and auditability.

## Prompt

# Goal
Generate a concise, professional, insurer-facing progress update message to be sent every 3 business days during a household property insurance claim process.

# Constraints & Style
- Must include: (1) clear reference to the original报案号 (claim report number), (2) date range covered, (3) verifiable actions completed (e.g., 'submitted photos of water-damaged flooring on 2024-09-05', 'received signed statement from property manager'), (4) pending items with owner and deadline, (5) explicit request for insurer’s confirmation or next-step instruction.
- Must NOT include: speculative statements, emotional language, unverified claims, internal notes, or raw evidence attachments — only reference them by type and timestamp.
- Tone: factual, cooperative, time-bound; avoid passive voice where accountability is assigned (e.g., 'We have submitted' not 'Submission was made').
- Format: single paragraph, ≤120 words; no bullet points or markdown.
- Language: match user’s primary language (e.g., Chinese if user communicates in Chinese).

# Workflow
1. Extract latest claim report number and start date from user-provided context or prior messages.
2. Identify all completed, timestamped actions within the past 3 business days.
3. Identify all pending items with named owners and agreed deadlines.
4. Compose message adhering strictly to # Constraints & Style.
5. Output only the final message — no preamble, no explanations.

## Triggers

- 同步理赔进度
- 每三天更新保险公司
- 定期向保险公司汇报进展
- 理赔过程中的阶段性反馈
- 保险理赔进度通报
