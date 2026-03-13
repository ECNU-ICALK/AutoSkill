---
id: "78f47d10-0042-4ddd-8550-6c078eeebf2f"
name: "Deduplicate and Sort Bilingual Word Lists"
description: "Process a comma-separated list of mixed Russian and English words or collocations by removing duplicates and returning two alphabetically sorted lists."
version: "0.1.0"
tags:
  - "deduplication"
  - "sorting"
  - "bilingual"
  - "list processing"
  - "data cleaning"
triggers:
  - "remove duplicate words from the following set"
  - "give me two sets of words sorted alphabetically in Russian and English"
  - "deduplicate this list and sort it"
---

# Deduplicate and Sort Bilingual Word Lists

Process a comma-separated list of mixed Russian and English words or collocations by removing duplicates and returning two alphabetically sorted lists.

## Prompt

# Role & Objective
Process mixed-language text lists to deduplicate and organize them into specific language sets.

# Operational Rules & Constraints
1. Accept input as a set of words and collocations divided by commas.
2. Remove duplicate words from the set.
3. Separate the unique items into two distinct sets: Russian and English.
4. Sort each set alphabetically.
5. Output the two sets clearly labeled by language.

# Anti-Patterns
Do not add words that were not in the original list.
Do not merge languages unless specified.

## Triggers

- remove duplicate words from the following set
- give me two sets of words sorted alphabetically in Russian and English
- deduplicate this list and sort it
