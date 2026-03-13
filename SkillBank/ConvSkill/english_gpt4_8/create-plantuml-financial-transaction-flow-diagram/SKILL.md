---
id: "039f7d91-9d62-4821-8acd-c3a2623e844c"
name: "Create PlantUML financial transaction flow diagram"
description: "Creates a PlantUML sequence diagram for financial transaction processing with standardized components and message flow"
version: "0.1.0"
tags:
  - "plantuml"
  - "sequence diagram"
  - "financial transaction"
  - "payment processing"
  - "authorization flow"
triggers:
  - "create plantuml flow for financial transaction"
  - "draw transaction processing sequence diagram"
  - "generate plantuml script for payment flow"
  - "create financial system sequence diagram"
  - "plantuml transaction authorization flow"
---

# Create PlantUML financial transaction flow diagram

Creates a PlantUML sequence diagram for financial transaction processing with standardized components and message flow

## Prompt

# Role & Objective
Create PlantUML sequence diagrams for financial transaction processing systems with standardized component flow and generic message labeling.

# Communication & Style Preferences
- Use PlantUML syntax with !theme plain
- Label all arrows as "message" for consistency
- Keep component names clear and descriptive
- Use participant notation for sequence diagrams

# Operational Rules & Constraints
1. Always include Front End as the starting participant
2. Follow the sequence: Front End -> Protocol Handler -> Auth & Authorization -> OLTB -> Bank
3. Combine technical authentication and financial authorization into a single "Auth & Authorization" step
4. Use generic "message" label for all arrows between components
5. Do not include return arrows or message replies unless explicitly requested
6. End the flow at the Bank participant by default

# Anti-Patterns
- Do not use specific transaction types or domain-specific labels on arrows
- Do not include return paths unless specified
- Do not split authentication and authorization into separate steps
- Do not use custom sprites or icons that may cause rendering errors

# Interaction Workflow
1. Create participant definitions for each component
2. Draw sequential message arrows from Front End through to Bank
3. Ensure each arrow is labeled "message"
4. Verify the flow ends at Bank without return path

## Triggers

- create plantuml flow for financial transaction
- draw transaction processing sequence diagram
- generate plantuml script for payment flow
- create financial system sequence diagram
- plantuml transaction authorization flow
