---
id: "a503760f-a6a2-4815-8e58-6db56f42b3c2"
name: "runway-threshold-cost-control-trigger"
description: "A capability to automatically trigger cost-control measures when startup runway falls below a specified threshold (5 months), ensuring proactive financial sustainability."
version: "0.1.0"
tags:
  - "startup"
  - "financial"
  - "runway"
  - "cost-control"
  - "crisis-management"
triggers:
  - "runway drops below threshold"
  - "cash runway warning"
  - "cost control protocol activation"
---

# runway-threshold-cost-control-trigger

A capability to automatically trigger cost-control measures when startup runway falls below a specified threshold (5 months), ensuring proactive financial sustainability.

## Prompt

# Goal
When runway drops below 5 months, initiate cost-control measures to extend operational runway and prevent cash depletion.

# Constraints & Style
- Must trigger based on verified runway calculation (current cash ÷ monthly burn rate)
- Cost-control measures must be proportional to runway shortfall (4-5 months: moderate cuts; <4 months: aggressive cuts)
- Must document all cost-cutting actions and expected runway extension impact
- Must escalate immediately to CEO/Finance lead for approval
- Must implement within 72 hours of trigger and report results within one week

# Workflow
1. Monitor runway calculation weekly (CFO/Finance Lead responsibility)
2. If runway < 5 months: Trigger cost-control protocol
3. CFO to identify top 3 cost-cutting opportunities impacting ≥20% of burn rate
4. CEO to approve cost-control measures via emergency board review
5. Implement cost-control measures within 72 hours
6. Re-calculate runway and report back to board within 1 week

## Triggers

- runway drops below threshold
- cash runway warning
- cost control protocol activation
