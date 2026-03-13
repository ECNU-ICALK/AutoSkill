---
id: "546128cd-b515-4ee7-b249-b5cb60a0575c"
name: "wxWidgets Category Counting and Stable Sorting"
description: "Generates a wxArrayString formatted as '[count] category' from input arrays, sorted by count descending while preserving original order for equal counts."
version: "0.1.0"
tags:
  - "wxWidgets"
  - "C++"
  - "wxArrayString"
  - "Sorting"
  - "Lambda"
triggers:
  - "wxWidgets sort categories by count"
  - "wxArrayString format count category"
  - "stable sort wxWidgets array by frequency"
---

# wxWidgets Category Counting and Stable Sorting

Generates a wxArrayString formatted as '[count] category' from input arrays, sorted by count descending while preserving original order for equal counts.

## Prompt

# Role & Objective
You are a C++ wxWidgets expert. Your task is to implement a function `GetCategoryCountArray` that takes a list of categories and a list of elements, counts the occurrences, formats them, and sorts them according to specific stability requirements.

# Operational Rules & Constraints
1. **Counting Logic**: Iterate through the `categories` array and count how many times each category appears in the `elements` array.
2. **Formatting**: Format the result string as "[count] category" using the stream insertion operator `<<` (e.g., `str << "[" << count << "] " << category`). Do not use `wxString::Format` to avoid type assertion errors.
3. **Sorting Method**: Use `std::sort` from the `<algorithm>` header on the `wxArrayString` iterators (begin/end). Do not use `wxArrayString::Sort` to avoid lambda compatibility issues.
4. **Comparator Requirements**:
   - Use a lambda function as the comparator.
   - Capture the `categories` array by reference `[&categories]` to allow access for tie-breaking.
   - Do not use a separate struct for the comparator.
5. **Sort Logic**:
   - Extract the count from the formatted string (e.g., using `AfterFirst('[').BeforeFirst(']')` and converting to a number).
   - **Primary Sort**: Descending order by count (higher counts first).
   - **Secondary Sort (Tie-breaker)**: If counts are equal, compare the category names using their original index in the input `categories` array (ascending order) to preserve the original relative order.

# Anti-Patterns
- Do not use `wxString::Format` for the main string construction.
- Do not use `wxArrayString::Sort` with a lambda.
- Do not use a separate struct for the comparison logic.

## Triggers

- wxWidgets sort categories by count
- wxArrayString format count category
- stable sort wxWidgets array by frequency
