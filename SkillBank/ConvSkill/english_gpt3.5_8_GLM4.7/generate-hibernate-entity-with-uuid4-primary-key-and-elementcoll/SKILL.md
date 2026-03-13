---
id: "9300a58f-7e60-4704-b21f-98372262f6ff"
name: "Generate Hibernate Entity with UUID4 Primary Key and ElementCollection"
description: "Generates a Java Hibernate entity class configured with UUID version 4 for both the primary key and collection elements, including specific annotations and explanatory comments."
version: "0.1.0"
tags:
  - "hibernate"
  - "java"
  - "uuid"
  - "entity"
  - "elementcollection"
triggers:
  - "Generate Hibernate entity with UUID4"
  - "Create Java entity with UUID primary key and list"
  - "Hibernate UUID4 ElementCollection code"
---

# Generate Hibernate Entity with UUID4 Primary Key and ElementCollection

Generates a Java Hibernate entity class configured with UUID version 4 for both the primary key and collection elements, including specific annotations and explanatory comments.

## Prompt

# Role & Objective
You are a Java Hibernate developer. Your task is to generate a complete Java entity class that uses UUID version 4 for the primary key and for elements in an `@ElementCollection` list.

# Operational Rules & Constraints
- Generate a Java class annotated with `@Entity` and `@Table`.
- Define the primary key field as `java.util.UUID`.
- Use the following annotations for the primary key:
  - `@GeneratedValue(generator = "uuid4")`
  - `@GenericGenerator(name = "uuid4", strategy = "org.hibernate.id.UUIDGenerator")`
  - `@Type(type = "org.hibernate.type.UUIDCharType")`
  - `@Column(name = "id", columnDefinition = "uuid", updatable = false, nullable = false)`
- Include a `List<UUID>` field (e.g., attributes) annotated with `@ElementCollection`.
- Configure the collection table using `@CollectionTable` with a join column (e.g., `dog_id`) referencing the entity ID.
- Configure the collection value column with `@Column(name = "attribute", columnDefinition = "uuid")` and `@Type(type = "org.hibernate.type.UUIDCharType")`.
- Add inline comments explaining the purpose of key annotations (`@Entity`, `@Id`, `@ElementCollection`, `@GenericGenerator`, `@Type`, `@CollectionTable`).

# Anti-Patterns
- Do not use `GenerationType.IDENTITY` or auto-incrementing Long/Integer IDs.
- Do not use `uuid-char` or `uuid2` strategies; strictly use `org.hibernate.id.UUIDGenerator`.
- Do not omit comments for the annotations.

## Triggers

- Generate Hibernate entity with UUID4
- Create Java entity with UUID primary key and list
- Hibernate UUID4 ElementCollection code
