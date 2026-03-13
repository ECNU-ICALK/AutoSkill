---
id: "3b437934-a6a3-4e40-b9a5-5375b8486065"
name: "Python LogFile Context Manager with Specific Format"
description: "Generates a Python class `LogFile` inheriting from `ContextDecorator` to log execution start time, duration, and errors to a file using a strict pipe-delimited format."
version: "0.1.0"
tags:
  - "python"
  - "context-manager"
  - "logging"
  - "contextdecorator"
  - "code-generation"
triggers:
  - "create a logfile context manager"
  - "python logging context decorator"
  - "log start run error to file"
  - "contextdecorator logfile"
  - "create context manager log file specific format"
---

# Python LogFile Context Manager with Specific Format

Generates a Python class `LogFile` inheriting from `ContextDecorator` to log execution start time, duration, and errors to a file using a strict pipe-delimited format.

## Prompt

# Role & Objective
You are a Python developer. Your task is to implement a context manager class named `LogFile` that inherits from `ContextDecorator`. This class must log the execution details of a code block or function to a specified file.

# Operational Rules & Constraints
1. **Inheritance**: The class must inherit from `contextlib.ContextDecorator`.
2. **Initialization**: Accept `logfile_path` as an argument to specify the output file.
3. **Logging Content**: Every log entry must contain:
   - Start time (labeled "Start:")
   - Execution time/Duration (labeled "Run:")
   - Error information (labeled "An error occurred:")
4. **Output Format**: The log line must strictly follow this pipe-delimited format:
   `Start: {start_timestamp} | Run: {duration} | An error occurred: {error_message}`
5. **Error Handling**:
   - If no error occurs, `{error_message}` must be `None`.
   - If a `ZeroDivisionError` occurs, `{error_message}` must be `division by zero`.
   - For other exceptions, log the exception value.
6. **File Mode**: Open the file in append mode ("a+").

# Anti-Patterns
- Do not use the standard `logging` module configuration; write directly to the file object.
- Do not alter the specific labels ("Start:", "Run:", "An error occurred:") or the pipe separator structure.

## Triggers

- create a logfile context manager
- python logging context decorator
- log start run error to file
- contextdecorator logfile
- create context manager log file specific format
