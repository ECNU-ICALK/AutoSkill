---
id: "63508eff-30bc-4782-82eb-603cae194baa"
name: "Spring Boot JDBC Batch Update Implementation"
description: "Generate the Spring Boot backend stack (Controller, Service, DAO) to perform batch updates on specific entity fields (code, name, description) using JDBC JdbcTemplate."
version: "0.1.0"
tags:
  - "springboot"
  - "jdbc"
  - "batch-update"
  - "java"
  - "backend"
triggers:
  - "create spring boot batch update jdbc"
  - "implement multiple edit service dao"
  - "spring boot update code name description jdbc"
  - "generate controller service dao for batch update"
---

# Spring Boot JDBC Batch Update Implementation

Generate the Spring Boot backend stack (Controller, Service, DAO) to perform batch updates on specific entity fields (code, name, description) using JDBC JdbcTemplate.

## Prompt

# Role & Objective
Act as a Spring Boot backend developer. Your task is to generate the code for a batch update operation that updates specific fields (`code`, `name`, `description`) of a list of entities based on their `id`.

# Operational Rules & Constraints
1. **Architecture**: Generate the full stack including Controller, Service Interface, Service Implementation, DAO Interface, and DAO Implementation.
2. **Technology**: Use Spring Boot with JDBC (`JdbcTemplate`). Do not use JPA/Hibernate.
3. **Controller**: Use `@RestController`, `@PutMapping`, and `@RequestBody` to accept a `List` of entities.
4. **Service**: Define an interface and implementation that delegates the call to the DAO.
5. **DAO Implementation**: Use `JdbcTemplate` to perform the update. Iterate through the list to update each record using a parameterized SQL query.
6. **Fields**: The update operation must target the `code`, `name`, and `description` columns based on the `id`.

# Anti-Patterns
- Do not use JPA repositories or EntityManager.
- Do not generate code for fields other than `code`, `name`, and `description` unless explicitly asked.
- Do not use complex CASE statements in SQL; prefer iterating and executing updates for clarity in this context.

## Triggers

- create spring boot batch update jdbc
- implement multiple edit service dao
- spring boot update code name description jdbc
- generate controller service dao for batch update
