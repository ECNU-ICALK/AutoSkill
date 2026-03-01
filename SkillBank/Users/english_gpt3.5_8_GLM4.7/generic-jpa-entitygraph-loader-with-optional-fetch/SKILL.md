---
id: "2091c0ad-983b-4a16-a0af-3c12ad060500"
name: "Generic JPA EntityGraph Loader with Optional Fetch"
description: "Create a generic Java method using Hibernate/JPA to load all entities of a given type, with an option to eagerly fetch a specific association path via EntityGraph to prevent circular dependency errors."
version: "0.1.0"
tags:
  - "java"
  - "hibernate"
  - "jpa"
  - "entitygraph"
  - "eager-fetching"
triggers:
  - "modify loadAllData to use entity graph"
  - "generic hibernate loader with optional fetch"
  - "prevent stackoverflow in jpa query"
  - "create a generic method with entity graph argument"
---

# Generic JPA EntityGraph Loader with Optional Fetch

Create a generic Java method using Hibernate/JPA to load all entities of a given type, with an option to eagerly fetch a specific association path via EntityGraph to prevent circular dependency errors.

## Prompt

# Role & Objective
Act as a Java/Hibernate expert. Write a generic method `loadAllData` that retrieves all entities of a specified type using the JPA Criteria API.

# Operational Rules & Constraints
1. The method signature must be `public <T> List<T> loadAllData(Class<T> type, String association)`.
2. Use `CriteriaBuilder` and `CriteriaQuery` to construct the query.
3. If the `association` string is not empty, create an `EntityGraph` for the entity type and add the association node to it.
4. Apply the `EntityGraph` as a fetch graph hint (`javax.persistence.fetchgraph`) to the query.
5. Ensure the implementation handles circular dependencies correctly to avoid StackOverflowError (e.g., by using `addSubgraph` or `addAttributeNodes` appropriately).
6. Use `session.createQuery(criteria).unwrap(...).setHint(...)` if necessary to apply the hint correctly on the underlying query object.
7. If `association` is empty, load data without eager fetching any specific field.

# Anti-Patterns
- Do not use the non-existent `FetchGraph` type; use `EntityGraph`.
- Do not call `setHint` directly on `CriteriaQuery` if the API does not support it; unwrap to the underlying `Query` object if needed.

## Triggers

- modify loadAllData to use entity graph
- generic hibernate loader with optional fetch
- prevent stackoverflow in jpa query
- create a generic method with entity graph argument
