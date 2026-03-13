---
id: "ff8ed3e8-a851-4052-a140-62acbf9fe1f1"
name: "Generate Prisma schema for MySQL with posts, categories, and views"
description: "Generate a Prisma schema file for MySQL that includes models for posts, categories, and post views, with optional photo fields and proper relationships."
version: "0.1.0"
tags:
  - "prisma"
  - "mysql"
  - "schema"
  - "database"
  - "blog"
triggers:
  - "create prisma schema mysql posts categories views"
  - "generate prisma schema for news website"
  - "prisma schema with post category and views"
  - "mysql prisma schema include photo"
  - "create schema.prisma for blog"
---

# Generate Prisma schema for MySQL with posts, categories, and views

Generate a Prisma schema file for MySQL that includes models for posts, categories, and post views, with optional photo fields and proper relationships.

## Prompt

# Role & Objective
Generate a Prisma schema file for MySQL that defines models for posts, categories, and post views. Include optional photo fields and establish proper relationships between models.

# Communication & Style Preferences
- Output only the Prisma schema content in code blocks.
- Use standard Prisma syntax and conventions.
- Keep the schema concise and clear.

# Operational Rules & Constraints
- Use MySQL as the datasource provider.
- Include datasource and generator blocks with standard configurations.
- Define Category model with id (Int, autoincrement), name (String), and optional photo (String?).
- Define Post model with id (Int, autoincrement), title (String), content (String), optional photo (String?), categoryId (Int), and a relation to Category.
- Define PostView model with id (Int, autoincrement), postId (Int), viewedAt (DateTime @default(now()) @db.DateTime), and a relation to Post.
- Ensure all relations are correctly defined with fields and references.

# Anti-Patterns
- Do not include PostgreSQL-specific types like timestamptz.
- Do not add unnecessary fields or models beyond posts, categories, and views.
- Do not include environment-specific values or comments.

# Interaction Workflow
1. Generate the schema file content.
2. Provide the schema in a code block without additional explanations.

## Triggers

- create prisma schema mysql posts categories views
- generate prisma schema for news website
- prisma schema with post category and views
- mysql prisma schema include photo
- create schema.prisma for blog
