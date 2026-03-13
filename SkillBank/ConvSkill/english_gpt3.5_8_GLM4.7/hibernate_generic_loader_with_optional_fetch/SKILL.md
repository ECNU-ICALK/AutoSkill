---
id: "2091c0ad-983b-4a16-a0af-3c12ad060500"
name: "hibernate_generic_loader_with_optional_fetch"
description: "Create a generic Java method using Hibernate/JPA Criteria API to load all entities of a given type, conditionally applying a left-join fetch on a specified field to optimize loading and prevent N+1 issues."
version: "0.1.1"
tags:
  - "java"
  - "hibernate"
  - "criteria-api"
  - "left-join"
  - "generic-method"
triggers:
  - "modify loadAllData to use left join fetch"
  - "generic hibernate loader with optional fetch"
  - "java hibernate load all with join argument"
  - "create a generic method with optional field fetch"
  - "prevent n+1 with optional criteria fetch"
---

# hibernate_generic_loader_with_optional_fetch

Create a generic Java method using Hibernate/JPA Criteria API to load all entities of a given type, conditionally applying a left-join fetch on a specified field to optimize loading and prevent N+1 issues.

## Prompt

# Role & Objective
Act as a Java/Hibernate expert. Write a generic method `loadAllData` that retrieves all entities of a specified type using the JPA Criteria API.

# Operational Rules & Constraints
1. The method signature must be `public <T> List<T> loadAllData(Class<T> type, String fieldName)`.
2. Use `HibernateUtil.getSessionFactory().openSession()` to obtain a session.
3. Use `CriteriaBuilder` and `CriteriaQuery` to construct the query.
4. **Conditional Fetching Logic**:
   - If the `fieldName` argument is not an empty String, apply a left-join fetch using `root.fetch(fieldName, JoinType.LEFT)`.
   - If `fieldName` is empty, load data without applying any specific fetch (standard load).
5. Ensure the generic type `T` is handled correctly in the CriteriaQuery construction (e.g., using `criteria.select(root)`).
6. Return a `List<T>`.

# Anti-Patterns
- Do not use EntityGraph or query hints (`setHint`); use the Criteria API `fetch` method.
- Do not hardcode specific entity class names (e.g., AlphaClass, BetaClass) into the method logic.
- Do not use HQL or native SQL strings; use the Criteria API.
- Do not throw exceptions for empty `fieldName`; handle it gracefully by skipping the fetch.

## Triggers

- modify loadAllData to use left join fetch
- generic hibernate loader with optional fetch
- java hibernate load all with join argument
- create a generic method with optional field fetch
- prevent n+1 with optional criteria fetch
