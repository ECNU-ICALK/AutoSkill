---
id: "bbb0e30f-c1fd-49fa-b857-4c9d2cc4b8f3"
name: "Generate MySQL user_activity table and sample data"
description: "Create a MySQL table for user activity with specific schema and generate sample data including continuous, returning, and churned users with multiple actions per day."
version: "0.1.0"
tags:
  - "MySQL"
  - "DDL"
  - "DML"
  - "user activity"
  - "sample data"
triggers:
  - "create user_activity table with sample data"
  - "generate mysql script for user activity"
  - "populate user_activity table with test data"
  - "create table with userid last_login_time action client"
  - "generate sample data for continuous returning churned users"
---

# Generate MySQL user_activity table and sample data

Create a MySQL table for user activity with specific schema and generate sample data including continuous, returning, and churned users with multiple actions per day.

## Prompt

# Role & Objective
Generate a MySQL script to create a user_activity table and populate it with sample data for one month, ensuring multiple actions per user per day and including continuous, returning, and churned user patterns.

# Communication & Style Preferences
- Output only valid MySQL DDL and DML statements.
- Use clear comments to indicate user behavior patterns (continuous, returning, churned).
- Ensure timestamps are sequential and realistic.

# Operational Rules & Constraints
- Table schema must include: userid INT, last_login_time TIMESTAMP, <TOKEN> TIMESTAMP, action ENUM('login','send','update'), client ENUM('android','iOS','desktop').
- Generate at least 100 records.
- Include multiple same actions for the same user on the same day.
- Ensure some users are continuous (daily activity), returning (activity with gaps), and churned (stop after a period).
- Use NULL for <TOKEN> when it's the first activity for a user; otherwise reference the previous activity timestamp.

# Anti-Patterns
- Do not generate data only for 'login' actions; include 'send' and 'update'.
- Do not limit to a single user; include multiple users.
- Do not use unrealistic timestamps or intervals.

# Interaction Workflow
1. First, output the CREATE TABLE statement.
2. Then, output INSERT statements for sample data following the rules above.

## Triggers

- create user_activity table with sample data
- generate mysql script for user activity
- populate user_activity table with test data
- create table with userid last_login_time action client
- generate sample data for continuous returning churned users
