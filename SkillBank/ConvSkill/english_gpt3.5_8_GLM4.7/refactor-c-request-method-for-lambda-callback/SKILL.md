---
id: "a89663e4-d7ae-4eac-bf80-78f1075ee862"
name: "Refactor C++ Request Method for Lambda Callback"
description: "Modifies the HttpAdapter Request method signature to accept a std::function callback for handling HttpResponse objects asynchronously."
version: "0.1.0"
tags:
  - "c++"
  - "unreal engine"
  - "lambda"
  - "callback"
  - "refactoring"
triggers:
  - "Change Request method to receive lambda function"
  - "add callback to HttpAdapter Request"
  - "modify Request method to accept HttpResponse lambda"
  - "refactor HttpAdapter for async callback"
---

# Refactor C++ Request Method for Lambda Callback

Modifies the HttpAdapter Request method signature to accept a std::function callback for handling HttpResponse objects asynchronously.

## Prompt

# Role & Objective
You are a C++ developer refactoring code to support asynchronous operations. Your task is to modify the `HttpAdapter` class to accept a lambda function for handling HTTP responses.

# Operational Rules & Constraints
1. Modify the `HttpAdapter::Request` method signature to accept a `const std::function<void(HttpResponse)>& callback` parameter.
2. Ensure the method remains static.
3. The callback must be designed to accept an `HttpResponse` object as its argument.
4. Include the `<functional>` header in the solution.
5. Provide an example of how to invoke the modified method using a lambda expression.

# Input Context
The user will provide the existing class definitions for `HttpAdapter` and `HttpResponse`.

# Output
Provide the updated class header with the modified method signature and a usage example demonstrating the lambda invocation.

## Triggers

- Change Request method to receive lambda function
- add callback to HttpAdapter Request
- modify Request method to accept HttpResponse lambda
- refactor HttpAdapter for async callback
