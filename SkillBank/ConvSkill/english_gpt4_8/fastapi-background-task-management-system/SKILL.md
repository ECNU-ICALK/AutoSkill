---
id: "f8607dcd-9355-4f7d-b889-d38ac0991f3d"
name: "FastAPI Background Task Management System"
description: "Build an OOP-based background task management system for FastAPI with SQLAlchemy persistence, supporting task lifecycle control (start/pause/stop/restart) and state synchronization between memory and database."
version: "0.1.0"
tags:
  - "FastAPI"
  - "BackgroundTasks"
  - "SQLAlchemy"
  - "TaskManagement"
  - "OOP"
triggers:
  - "implement background task management system"
  - "create OOP task manager for FastAPI"
  - "build task lifecycle control with SQLAlchemy"
  - "design pause/resume background tasks"
  - "implement task state persistence"
---

# FastAPI Background Task Management System

Build an OOP-based background task management system for FastAPI with SQLAlchemy persistence, supporting task lifecycle control (start/pause/stop/restart) and state synchronization between memory and database.

## Prompt

# Role & Objective
You are implementing a background task management system for a FastAPI application using SQLAlchemy. The system must provide an object-oriented interface for task execution with database persistence and lifecycle control.

# Communication & Style Preferences
- Use clear, modular Python code with type hints
- Follow FastAPI and SQLAlchemy best practices
- Implement proper error handling and logging
- Use async/await patterns where appropriate

# Operational Rules & Constraints
1. Define TaskStatus enum with: PENDING, RUNNING, PAUSED, FINISHED, FAILED
2. Create BackgroundTaskModel SQLAlchemy model with fields: id, task_name, status, start_time, end_time, result, last_run_time
3. Implement CRUD functions: create_task, get_task, get_all_tasks, update_task
4. Design BaseTask abstract class with methods: pre(), run(), post(), start(), pause(), stop(), restart()
5. Create TaskManager class that:
   - Maintains in-memory task registry
   - Loads active tasks from database on startup
   - Maps task names to task classes
   - Handles task lifecycle operations
6. All task state changes must be persisted to database immediately
7. Task execution should use threading for non-blocking operation
8. Support task resumption after application restart

# Anti-Patterns
- Do not use external task queues like Celery/RQ
- Do not block the FastAPI event loop
- Do not store task objects directly in database
- Do not use global variables for task management

# Interaction Workflow
1. On application startup, TaskManager loads tasks with status RUNNING or PAUSED from DB
2. Endpoints use TaskManager to create and start new tasks
3. TaskManager creates DB record, instantiates task object, and starts execution
4. Task methods update DB status at each lifecycle stage
5. Clients can query task status through endpoints that read from DB

## Triggers

- implement background task management system
- create OOP task manager for FastAPI
- build task lifecycle control with SQLAlchemy
- design pause/resume background tasks
- implement task state persistence
