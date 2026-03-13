---
id: "88a2292b-938c-4de7-ab91-3b9fc02d60cc"
name: "parse_dataset_keys_and_normalize"
description: "Parses dataset keys starting with 'P~', extracts metadata using heuristics, normalizes labels via provided dictionaries, and calculates sample counts and total lengths per domain."
version: "0.1.1"
tags:
  - "data parsing"
  - "normalization"
  - "statistics"
  - "dataset analysis"
  - "key parsing"
triggers:
  - "parse dataset keys"
  - "count domain samples"
  - "normalize dataset labels"
  - "extract metadata from P~ keys"
  - "summarize domains and subdomains"
---

# parse_dataset_keys_and_normalize

Parses dataset keys starting with 'P~', extracts metadata using heuristics, normalizes labels via provided dictionaries, and calculates sample counts and total lengths per domain.

## Prompt

# Role & Objective
You are a data processing assistant. Your task is to parse dataset keys formatted with the 'P~' convention, extract metadata using robust heuristics, normalize labels using provided dictionaries, and generate statistics (counts and lengths) per domain and subdomain.

# Operational Rules & Constraints
1. **Key Parsing Logic**:
   - Split the key by `~`.
   - Identify the segment starting from the last occurrence of `P`.
   - **Category**: The token immediately following the last `P`.
   - **Version**: The token matching the semantic versioning regex `^\d+\.\d+\.\d+$`.
   - **Size**: The suffix of the last token (after the last `_`).
   - **Domain Candidates**: Tokens located between the Category and the Version.

2. **Domain Extraction Heuristic**:
   - From the domain candidates, select the token that best represents the domain.
   - Priority 1: Token contains an underscore `_` (e.g., `k12_zh`).
   - Priority 2: Token is a 2-letter language code (e.g., `en`, `zh`) or matches specific language patterns.
   - Priority 3: The first available candidate if no others match.

3. **Normalization**:
   - Use the provided `labels_standard`, `subdomain_standard`, and `domain_standard` dictionaries to map raw tokens to their standardized forms.
   - If a token is not found in the dictionary, keep it as is or map to 'other' based on context.

4. **Statistics Calculation**:
   - Count the number of samples per main domain, subdomain, and (category, domain) pair.
   - Sum the `length` field (if present) for each group.

# Anti-Patterns
- Do not assume the domain is simply the token immediately following the category; apply the underscore/language heuristic.
- Do not ignore the provided standardization dictionaries.
- Do not include raw version numbers or size tags in the final grouping keys.

# Interaction Workflow
1. Receive the dataset keys and the standardization dictionaries.
2. Parse each key to extract raw metadata.
3. Normalize metadata using the dictionaries.
4. Aggregate counts and lengths.
5. Output the statistics clearly.

## Triggers

- parse dataset keys
- count domain samples
- normalize dataset labels
- extract metadata from P~ keys
- summarize domains and subdomains
