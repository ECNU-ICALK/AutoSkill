---
id: "56be2984-8009-4d46-80ca-cb7c84d4beaa"
name: "c-quick-sort-with-line-by-line-comments"
description: "Generates a C-language quicksort implementation where every executable line is annotated with a clear, pedagogically precise comment explaining its purpose and logic — designed for learning, code review, or onboarding. Applies to any request for 'C quicksort' followed by 'add comments per line' or 'explain each line'."
version: "0.1.0"
tags:
  - "c"
  - "algorithms"
  - "quicksort"
  - "code-commenting"
  - "education"
  - "beginner-friendly"
triggers:
  - "add comments to every line"
  - "explain each line in C quicksort"
  - "line-by-line annotated quicksort in C"
  - "teach me quicksort with full comments"
  - "C quicksort for learning"
---

# c-quick-sort-with-line-by-line-comments

Generates a C-language quicksort implementation where every executable line is annotated with a clear, pedagogically precise comment explaining its purpose and logic — designed for learning, code review, or onboarding. Applies to any request for 'C quicksort' followed by 'add comments per line' or 'explain each line'.

## Prompt

# Goal
Generate a complete, compilable, C89-compliant quicksort implementation (in-place, ascending order) with **a dedicated comment on every non-blank, non-brace line**, written in plain, precise English — no jargon without explanation, no implicit assumptions.

# Constraints & Style
- ✅ Every line containing code (e.g., `int i = low - 1;`, `swap(&arr[i], &arr[j]);`, `return i + 1;`) MUST have a corresponding `//` comment on the same line or immediately above it.
- ✅ Comments must explain *what the line does* AND *why it matters in the algorithm* (e.g., not just "increment i", but "increment i to expand the region of elements ≤ pivot").
- ✅ No comment may assume reader knows partitioning logic — define terms like 'pivot', 'partition index', 'in-place' explicitly where first used.
- ✅ All comments must be in English, even if user speaks another language — because C syntax and standard library names are English, and clarity trumps localization here.
- ✅ Include at least three self-contained, runnable test cases in `main()` covering: (1) typical unsorted array, (2) array with duplicates, (3) edge case (empty or single-element — handled safely via guard).
- ❌ Do NOT use C99+ features (e.g., `//` comments are allowed *only* for annotations — variable declarations must be at block start; no `for (int i...)` in loop head).
- ❌ Do NOT omit null/length guards in public-facing wrapper (`quick_sort_array`).
- ❌ Do NOT compress multiple statements onto one line.

# Workflow
- Step 1: Define `swap()` helper with explanatory comment.
- Step 2: Implement `partition()` with line-by-line comments — each assignment, loop, condition, and swap explained in context of Lomuto scheme.
- Step 3: Implement recursive `quick_sort()` with comments clarifying base case, pivot index usage, and subarray bounds.
- Step 4: Provide safe wrapper `quick_sort_array()` with explicit NULL/n check and comment on why it’s needed.
- Step 5: Write `main()` with three minimal, clearly labeled test arrays and inline `printf` output — each test case documented with expected behavior.

## Triggers

- add comments to every line
- explain each line in C quicksort
- line-by-line annotated quicksort in C
- teach me quicksort with full comments
- C quicksort for learning
