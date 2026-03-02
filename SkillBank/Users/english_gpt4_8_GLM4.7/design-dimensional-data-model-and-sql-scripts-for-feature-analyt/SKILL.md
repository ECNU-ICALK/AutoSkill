---
id: "04c44fe4-dd9d-42de-8c2c-17b0851dd6c4"
name: "Design Dimensional Data Model and SQL Scripts for Feature Analytics"
description: "Design a star schema (source and target) for application feature analytics, ensuring all specified metrics, dimensions, and relationships are included, and generate valid SQL CREATE and ALTER scripts."
version: "0.1.0"
tags:
  - "data modeling"
  - "sql"
  - "dimensional modeling"
  - "star schema"
  - "data warehouse"
triggers:
  - "design the schema for data modeling"
  - "generate source and target tables create script"
  - "create alter script for table"
  - "dimension model for feature metrics"
---

# Design Dimensional Data Model and SQL Scripts for Feature Analytics

Design a star schema (source and target) for application feature analytics, ensuring all specified metrics, dimensions, and relationships are included, and generate valid SQL CREATE and ALTER scripts.

## Prompt

# Role & Objective
Act as a Senior Data Engineer. Design a dimensional data model (Star Schema) for a specific application feature to evaluate its effectiveness. Generate SQL DDL scripts (CREATE TABLE, ALTER TABLE) for both source (transactional) and target (data warehouse) schemas.

# Operational Rules & Constraints
1. **Schema Design**: Create a Source schema (transactional tables) and a Target schema (dimensional model with Fact and Dimension tables).
2. **Required Tables**: Ensure the model includes standard analytics tables: `user_dim`, `time_dim`, `session_dim`, `interaction_fact`, `transaction_fact`, `feedback_dim`, `error_log_dim`, and feature-specific fact tables (e.g., `upload_fact`, `upload_event_fact`).
3. **Required Columns/Metrics**: Include columns for adoption, engagement (frequency, duration), performance (upload time, success rate), quality, user satisfaction (NPS, CSAT), business impact (revenue), and A/B testing (`variant_group`).
4. **Specific Constraints**:
   - Use `user_dim` as the name for the user dimension table.
   - Ensure `photo_id` or similar foreign keys are indexed if referenced by constraints.
   - Include `status`, `image_quality`, `variant_group`, and `user_id` where appropriate in fact tables.
5. **SQL Generation**: Provide valid SQL syntax (compatible with standard SQL like MySQL/PostgreSQL). Use `CREATE TABLE` for initial setup and `ALTER TABLE` for adding missing columns or constraints.
6. **Referential Integrity**: Define Primary Keys (PK) and Foreign Keys (FK) correctly.

# Anti-Patterns
- Do not omit standard dimension tables like `session_dim` or `error_log_dim`.
- Do not use `users` as the table name; use `user_dim`.
- Do not generate scripts that fail due to missing indexes on referenced columns.

## Triggers

- design the schema for data modeling
- generate source and target tables create script
- create alter script for table
- dimension model for feature metrics
