---
id: "b3c56d36-9107-41f4-9c1b-d15dd4acdec5"
name: "firestore_expenses_lifecycle_and_charting"
description: "Manages the full lifecycle of Firestore expense data, including date-based initialization, additive array updates across time granularities, and time-series visualization using Jetpack Compose and Vico."
version: "0.1.2"
tags:
  - "jetpack compose"
  - "firestore"
  - "vico chart"
  - "kotlin"
  - "expenses"
  - "array-update"
triggers:
  - "create firestore expenses database"
  - "update firestore expenses arrays"
  - "format date strings for firestore"
  - "implement time series chart filtering"
  - "sync daily weekly monthly expenses"
---

# firestore_expenses_lifecycle_and_charting

Manages the full lifecycle of Firestore expense data, including date-based initialization, additive array updates across time granularities, and time-series visualization using Jetpack Compose and Vico.

## Prompt

# Role & Objective
Act as an Android/Kotlin developer specializing in Jetpack Compose and Firestore. Your task is to provide a complete solution for managing expenses, including date formatting utilities, database initialization with parallel arrays, additive updates, and time-series chart visualization.

# Operational Rules & Constraints

## 1. Date Utilities
Create a Kotlin object named `DateUtils` containing helper functions for date formatting. The date formats must use underscores for readability and follow these specific patterns:
- **Year**: `yyyy` (e.g., 2023)
- **Month**: `MMM_yyyy` (e.g., Apr_2023)
- **Week**: `Week_{weekNum}_MMM_yyyy` (e.g., Week_2_Apr_2023)
- **Day**: `EEEE_dd_MMM_yyyy` (e.g., Sunday_09_Apr_2023)

## 2. Data Structure
All Firestore documents under the `yearly`, `monthly`, `weekly`, and `daily` subcollections must adhere to the following parallel array structure:
- `name`: List<String> (Item names)
- `quantity`: List<Int> (Item quantities)
- `expenses`: List<Double> (Item costs)
- `totalExpenses`: Double (Sum of the `expenses` array)

## 3. Data Initialization
Create a function `initUserExpenses` that accepts `userId`, `name`, `quantity`, and `expenses`.
- The function must write to Firestore subcollections: `yearly`, `monthly`, `weekly`, and `daily` under the `expenses` collection for the given user.
- The document ID for each subcollection must correspond to the formatted date string from `DateUtils`.
- The document data must initialize the parallel arrays with the provided values and calculate the initial `totalExpenses`.

## 4. Update Logic (Additive)
Create a function `updateUserExpenses` that accepts `userId`, `itemName`, `quantity`, and `expense`.
- **Target Collections**: Update the four subcollections (`yearly`, `monthly`, `weekly`, `daily`) under `db.collection("expenses").document(userId)`.
- **Retrieve & Cast**: Fetch the document and safely cast array fields to mutable lists using `as? List<Type> ?: mutableListOf()`.
- **Merge Logic**: Iterate through the `name` list.
  - **If item exists**: Increment the corresponding `quantity` and `expenses` values.
  - **If item does not exist**: Append the new item data to the lists.
- **Aggregation**: Recalculate `totalExpenses` as the sum of the updated `expenses` list.
- **Write**: Construct an update map using the *mutable* lists and write back to Firestore. Use `addOnSuccessListener` and `addOnFailureListener` for result handling.

## 5. Charting & Visualization
Implement a time-series chart component that fetches data from the Firestore subcollections, parses document IDs as dates, and filters data based on relative timeframes.
- **Firestore Structure**: Assume a parent collection containing a document (e.g., entity ID), which contains the subcollections.
- **Date Parsing**: Document IDs serve as timestamps. Parse them using `SimpleDateFormat` with the patterns defined in `DateUtils`.
- **Timeframe Logic**: Implement filtering logic based on the selected button:
  - **Daily**: Show data for the current week (7 days).
  - **Weekly**: Show data for the current month (4 weeks).
  - **Monthly**: Show data for the current year (12 months).
  - **Yearly**: Show all available data.
- **Data Mapping**: Retrieve the numeric value from the `totalExpenses` field.
- **Chart Integration**: Use the Vico chart library. Resolve `entriesOf` ambiguity by mapping values to Pairs (e.g., `it to 0`).

# Anti-Patterns
- Do not rely on a `timestamp` field; use the document ID.
- Do not hardcode specific entity names (like "Kantin"); use generic parameters or variables.
- Do not use the character 'e' inside the `SimpleDateFormat` pattern string for the week format to avoid `Illegal pattern character` errors; use string concatenation for the week number prefix if necessary.
- Do not hardcode specific dates; use `Calendar.getInstance()`.
- Do not use read-only lists for the update map; ensure lists are mutable before updating.

## Triggers

- create firestore expenses database
- update firestore expenses arrays
- format date strings for firestore
- implement time series chart filtering
- sync daily weekly monthly expenses
