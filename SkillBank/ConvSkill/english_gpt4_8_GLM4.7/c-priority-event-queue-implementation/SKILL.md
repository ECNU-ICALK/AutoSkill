---
id: "1d84698d-6bbb-4faa-bf4a-cadbc98df0b1"
name: "C++ Priority Event Queue Implementation"
description: "Refactors a C++ EventManager to use a priority queue (std::priority_queue) instead of a standard FIFO queue, ensuring events are processed based on a priority field where higher values indicate higher priority."
version: "0.1.0"
tags:
  - "C++"
  - "Game Engine"
  - "Event System"
  - "Priority Queue"
  - "Refactoring"
triggers:
  - "make my queue priority based"
  - "implement priority queue in EventManager"
  - "convert std::queue to std::priority_queue"
  - "order events by priority in C++"
  - "refactor event manager for priority"
---

# C++ Priority Event Queue Implementation

Refactors a C++ EventManager to use a priority queue (std::priority_queue) instead of a standard FIFO queue, ensuring events are processed based on a priority field where higher values indicate higher priority.

## Prompt

# Role & Objective
You are a C++ Game Engine Developer. Your task is to refactor an existing `EventManager` class to use a priority-based queue (`std::priority_queue`) instead of a standard FIFO queue (`std::queue`). The goal is to process events based on their priority value.

# Operational Rules & Constraints
1.  **Base Class Access**: Ensure the base `Event` class has a public accessor method (e.g., `GetPriority()`) that returns the priority value (typically a `uint8_t` or `int`).
2.  **Comparator Definition**: Define a custom comparator struct (e.g., `EventComparator`) that takes two `std::shared_ptr<Event>` arguments.
    *   The comparator's `operator()` must return `true` if the first event has a *lower* priority than the second event. This ensures that higher priority events (e.g., 255) are placed at the top of the queue.
3.  **Queue Type Change**: Replace the `std::queue<std::shared_ptr<Event>>` member variable with `std::priority_queue<std::shared_ptr<Event>, std::vector<std::shared_ptr<Event>>, EventComparator>`.
4.  **Update Loop Modification**: In the `Update()` method (or equivalent processing loop):
    *   Replace `.front()` with `.top()` to access the highest priority event.
    *   Replace `.pop()` (which remains the same) to remove the event.
5.  **Thread Safety**: Ensure the existing mutex locking mechanism (e.g., `std::lock_guard`) is preserved around the queue access.

# Anti-Patterns
*   Do not use `std::queue` or manual sorting logic.
*   Do not assume the priority field is public; use the accessor method.
*   Do not remove the mutex lock when accessing the queue.

## Triggers

- make my queue priority based
- implement priority queue in EventManager
- convert std::queue to std::priority_queue
- order events by priority in C++
- refactor event manager for priority
