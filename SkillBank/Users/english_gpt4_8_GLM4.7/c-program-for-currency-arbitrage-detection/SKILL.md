---
id: "73f64b79-4757-47a5-ad07-4563db4b6036"
name: "C Program for Currency Arbitrage Detection"
description: "Solve the currency arbitrage problem in C by finding the shortest sequence of exchanges that yields a profit greater than 1 percent, given a conversion matrix."
version: "0.1.0"
tags:
  - "c programming"
  - "arbitrage"
  - "algorithm"
  - "graph theory"
  - "currency conversion"
triggers:
  - "write a c program for arbitrage"
  - "solve the currency arbitrage problem"
  - "find profitable currency exchange sequence"
  - "c code for arbitrage detection"
  - "implement arbitrage algorithm in c"
---

# C Program for Currency Arbitrage Detection

Solve the currency arbitrage problem in C by finding the shortest sequence of exchanges that yields a profit greater than 1 percent, given a conversion matrix.

## Prompt

# Role & Objective
You are a C programmer tasked with solving the Arbitrage problem. You must write a C program that reads currency conversion tables and determines if a sequence of exchanges yields a profit of more than 1 percent.

# Operational Rules & Constraints
1. **Input Format**:
   - Read an integer `n` (2 <= n <= 20) representing the number of currencies.
   - Read `n` lines following `n`, each containing `n` conversion rates.
   - The diagonal elements are missing in the input but should be treated as 1.0.
   - The input may contain multiple tables; process until EOF.

2. **Logic Requirements**:
   - A valid arbitrage sequence must start and end with the same currency.
   - The profit must be strictly greater than 1.01 (1 percent).
   - The sequence must consist of `n` or fewer transactions.
   - If multiple profitable sequences exist, you must print the one with the **minimal length** (fewest exchanges).

3. **Output Format**:
   - If a profitable sequence exists, print the sequence of integers (1-indexed) representing the countries, separated by spaces. The sequence must start and end with the same integer.
   - If no sequence exists, print exactly: `no arbitrage sequence exists`.

# Anti-Patterns
- Do not print "arbitrage" or just "yes/no". You must print the specific sequence or the failure message.
- Do not stop at the first found sequence if it is not the shortest one.
- Ensure the code handles standard input/output correctly (scanf/printf).

## Triggers

- write a c program for arbitrage
- solve the currency arbitrage problem
- find profitable currency exchange sequence
- c code for arbitrage detection
- implement arbitrage algorithm in c
