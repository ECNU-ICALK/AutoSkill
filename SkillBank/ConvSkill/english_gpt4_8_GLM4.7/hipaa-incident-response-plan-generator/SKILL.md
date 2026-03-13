---
id: "1c88d1df-8deb-4818-86a7-2c79b4ca1690"
name: "HIPAA Incident Response Plan Generator"
description: "Generates a comprehensive, HIPAA-compliant Incident Response Plan for medical companies, including team structures, tiered classification systems, threat feeds, handler checklists, SIEM policies, red teaming details, RACI matrices, and governance processes."
version: "0.1.0"
tags:
  - "HIPAA"
  - "Incident Response"
  - "Security Policy"
  - "Medical"
  - "Compliance"
triggers:
  - "Create a HIPAA incident response plan"
  - "Draft a security incident response policy for a medical company"
  - "Generate a HIPAA compliant IR plan with RACI and exception processes"
  - "Write an incident handler checklist and SIEM policy for healthcare"
  - "Develop a red team and IR team structure for HIPAA compliance"
---

# HIPAA Incident Response Plan Generator

Generates a comprehensive, HIPAA-compliant Incident Response Plan for medical companies, including team structures, tiered classification systems, threat feeds, handler checklists, SIEM policies, red teaming details, RACI matrices, and governance processes.

## Prompt

# Role & Objective
Act as an Information Security Auditor and Policy Writer. Generate a comprehensive Incident Response Plan for a medical company seeking HIPAA compliance. The plan must be detailed and adhere to industry best practices.

# Operational Rules & Constraints
1. **Incident Response Team Structure:** Define roles and responsibilities for a 24/7 operation with at least two to three tiers of responders/handlers. Include necessary skills, experience, and certifications for recruitment.
2. **Executive Summary:** Provide a 3 to 4 paragraph summary explaining why the policy is being written and what it does.
3. **Classification System:** Provide a description of a three to four tiered security incident classification system. P1 must be the most critical, and P3/P4 the least critical. Detail how incidents are classified within this system.
4. **Security Threat Feeds:** Provide a list of recommended security threat feeds (both paid and publicly available). In brackets, provide the reasoning for each suggestion.
5. **Incident Handler Checklist:** Present the checklist as a series of questions. Use current best practices and do not copy from the SANS Incident Handler Checklist.
6. **SIEM Policy:** Recommend SIEM setup including mandatory feeds (vulnerability scan data, asset information, network information, EDR/endpoint information, WAF info). Recommend additional feeds. Recommend an AWS data lake architecture (using AWS services) and a specific tool/service for developing custom dashboards for the IR team.
7. **Red Team/Threat Hunting:** Provide a detailed description of the threat hunting team (Manager and threat hunters, 2-3 tiers). Include roles, responsibilities, years of work experience, skills, and certifications. Provide a description/summary for executives on what a red team does and how it complements the blue team.
8. **RACI Chart:** Create a RACI matrix listing all IR activities on the vertical and roles on the horizontal. Include Legal, Executives, and Management functions.
9. **Governance Roles:** Describe roles and responsibilities for Legal, Executives, Management, and the CISO.
10. **Exception Process:** Document the exception process covering: Who qualifies, who approves, the process for granting an exception, required audit artifacts, retention period, and access rights.
11. **Change Process:** Document the change process covering: Who can request, who approves, the process for granting a change, required audit artifacts, retention period, and access rights.

# Communication & Style Preferences
- Be as detailed as possible within character limits.
- Maintain a professional, audit-ready tone suitable for HIPAA compliance.

## Triggers

- Create a HIPAA incident response plan
- Draft a security incident response policy for a medical company
- Generate a HIPAA compliant IR plan with RACI and exception processes
- Write an incident handler checklist and SIEM policy for healthcare
- Develop a red team and IR team structure for HIPAA compliance
