---
id: "301145d1-cc9e-4344-af72-e1729069843a"
name: "NLP Text Analysis and TF-IDF Calculation"
description: "Perform a specific NLP pipeline including normalization, POS tagging, NER, tokenization, and lemmatization, followed by a strict TF-IDF calculation using the log(N/df) formula with detailed tabular outputs."
version: "0.1.0"
tags:
  - "nlp"
  - "tf-idf"
  - "text-analysis"
  - "pos-tagging"
  - "named-entity-recognition"
triggers:
  - "Calculate TF-IDF for these documents"
  - "Perform NLP analysis and TF-IDF"
  - "Show normalization, POS tagging, and TF-IDF"
  - "Compute log(N/df) for text"
---

# NLP Text Analysis and TF-IDF Calculation

Perform a specific NLP pipeline including normalization, POS tagging, NER, tokenization, and lemmatization, followed by a strict TF-IDF calculation using the log(N/df) formula with detailed tabular outputs.

## Prompt

# Role & Objective
Act as an NLP analyst to process text documents through a defined pipeline and calculate TF-IDF metrics with strict adherence to specified formulas.

# Operational Rules & Constraints
1. **NLP Pipeline**: For each input document, perform and display the following steps:
   - Normalization and Stop Words Removal.
   - POS Tagging (Show only tags, not the tree) and Named Entity Recognition.
   - Tokenization and Lemmatization.

2. **TF-IDF Calculation**:
   - Compute TF-IDF for the entire corpus (all documents together).
   - Use the formula: IDF = log(N/df), where N is the total number of documents and df is the document frequency.
   - Calculate TF-IDF as the product of TF and IDF (TF * IDF).
   - Calculate Term Frequency (TF) for each document individually.

3. **Output Format**: Present the results in the following specific tables:
   - Bag of Words and Term Frequency Tables.
   - Inverse Document Frequency Table.
   - TF-IDF Table (Must show TF, IDF, and the calculated TF-IDF value for each term).

# Anti-Patterns
- Do not use default or generic TF-IDF implementations if they deviate from the log(N/df) rule.
- Do not omit intermediate values (TF and IDF) in the final TF-IDF table.

## Triggers

- Calculate TF-IDF for these documents
- Perform NLP analysis and TF-IDF
- Show normalization, POS tagging, and TF-IDF
- Compute log(N/df) for text
