---
id: "c3e6ef42-b521-4933-9c43-cdff5edd5b30"
name: "Firestore Expense Schema Design"
description: "Design a Firestore database schema for an expense tracker with a specific hierarchy (Expenses -> Months -> Days) and item structure (name, quantity, price), supporting multiple items per day."
version: "0.1.0"
tags:
  - "firestore"
  - "database"
  - "schema"
  - "expenses"
  - "android"
triggers:
  - "firestore expense schema"
  - "database schema for expenses"
  - "firestore monthly daily structure"
  - "design expense database"
---

# Firestore Expense Schema Design

Design a Firestore database schema for an expense tracker with a specific hierarchy (Expenses -> Months -> Days) and item structure (name, quantity, price), supporting multiple items per day.

## Prompt

# Role & Objective
Design a Firestore database schema for an expense tracking application based on the user's specific hierarchical and data type requirements.

# Operational Rules & Constraints
- **Root Collection**: The parent collection must be named 'expenses'.
- **Hierarchy**: The structure must be organized as: Expenses -> 12 Months -> Days.
- **Day Documents**: Each day (e.g., 'Sunday_09_Apr_2023') acts as a document.
- **Data Structure**: Each day document must store multiple items.
- **Item Fields**: Each item must consist of:
  - `name`: String
  - `quantity`: Int
  - `price`: Double
- **Multi-value Storage**: Since each day contains multiple items, the fields (name, quantity, price) must be capable of storing multiple values (e.g., using arrays).

# Output Contract
Provide the Firestore schema structure, illustrating the collection/document paths and the data types for the fields.

## Triggers

- firestore expense schema
- database schema for expenses
- firestore monthly daily structure
- design expense database
