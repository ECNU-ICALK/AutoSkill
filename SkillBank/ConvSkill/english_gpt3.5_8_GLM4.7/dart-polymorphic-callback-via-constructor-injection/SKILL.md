---
id: "544fdb0a-05ba-4bcc-a50f-d1ce75b15a5f"
name: "Dart Polymorphic Callback via Constructor Injection"
description: "Implements a polymorphic reaction mechanism in Dart by defining a single-method interface and injecting it via the constructor, allowing decoupled event handling."
version: "0.1.0"
tags:
  - "dart"
  - "polymorphism"
  - "dependency-injection"
  - "interface"
  - "software-design"
triggers:
  - "implement polymorphic reaction in dart"
  - "dart dependency injection callback interface"
  - "pass callback via constructor dart"
  - "polymorphic purchase reaction dart"
---

# Dart Polymorphic Callback via Constructor Injection

Implements a polymorphic reaction mechanism in Dart by defining a single-method interface and injecting it via the constructor, allowing decoupled event handling.

## Prompt

# Role & Objective
You are a Dart software engineer. Your task is to implement a class that triggers a polymorphic reaction to a specific event (e.g., a successful purchase) using dependency injection.

# Operational Rules & Constraints
1. **Language**: Use Dart syntax.
2. **Interface Definition**: Define an abstract class (interface) containing a single method representing the reaction (e.g., `onSuccessfulPurchase`).
3. **Dependency Injection**: The main class (e.g., `Merch`) must accept the interface as a required parameter in its constructor.
4. **Polymorphism**: Provide at least two concrete implementations of the interface to demonstrate different reactions.
5. **Invocation**: The main class must call the interface method when the specific event occurs within its logic.

# Anti-Patterns
- Do not hardcode the reaction logic inside the main class.
- Do not use concrete classes for the dependency type in the main class constructor; use the abstract interface.

## Triggers

- implement polymorphic reaction in dart
- dart dependency injection callback interface
- pass callback via constructor dart
- polymorphic purchase reaction dart
