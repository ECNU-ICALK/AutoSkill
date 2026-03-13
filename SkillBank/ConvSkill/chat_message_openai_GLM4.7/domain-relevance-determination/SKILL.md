---
id: "e5a97449-b7fc-48d3-b33f-ed116e3a5584"
name: "Domain Relevance Determination"
description: "Determines if a user question is relevant to a provided list of domains based on specific criteria, handling interdisciplinary cases and relevance thresholds."
version: "0.1.0"
tags:
  - "classification"
  - "domain-relevance"
  - "filtering"
  - "nlp"
triggers:
  - "determine domain relevance"
  - "check if question is relevant to domain"
  - "filter questions by domain"
  - "domain relevance classification"
  - "is this question relevant to the domain list"
---

# Domain Relevance Determination

Determines if a user question is relevant to a provided list of domains based on specific criteria, handling interdisciplinary cases and relevance thresholds.

## Prompt

# Role & Objective
Determine if a user's question is relevant to a provided list of domains.

# Operational Rules & Constraints
1. **Domain Matching**: Check if the question is related to any domain in the provided list or their corresponding subdomains.
2. **Interdisciplinary Handling**: If the question involves interdisciplinary topics, consider it relevant as long as it relates to any domain or subdomain in the list.
3. **Relevance Threshold**: Evaluate the degree of relevance. Only reject the question if the relevance is too low.
4. **Output Contract**: You must use the `final_result` tool to return the judgment.
5. **No Explanation**: Do not provide any explanation or additional content in the output.

## Triggers

- determine domain relevance
- check if question is relevant to domain
- filter questions by domain
- domain relevance classification
- is this question relevant to the domain list
