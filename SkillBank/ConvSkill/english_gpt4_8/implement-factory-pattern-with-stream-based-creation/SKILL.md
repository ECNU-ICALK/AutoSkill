---
id: "99073754-dc2b-40c2-9fb3-850fbea7018f"
name: "Implement Factory Pattern with Stream-based Creation"
description: "Extend a factory pattern to support creating objects from input streams while maintaining type safety and avoiding if-else chains. Use separate callback maps for parameterless and stream-based creation."
version: "0.1.0"
tags:
  - "factory pattern"
  - "deserialization"
  - "C++"
  - "stream processing"
  - "object creation"
triggers:
  - "extend factory to support file deserialization"
  - "implement CreateFigureFromFile with factory pattern"
  - "add stream-based creation to factory"
  - "factory pattern with two callback maps"
---

# Implement Factory Pattern with Stream-based Creation

Extend a factory pattern to support creating objects from input streams while maintaining type safety and avoiding if-else chains. Use separate callback maps for parameterless and stream-based creation.

## Prompt

# Role & Objective
You are implementing an extension to a factory pattern that supports creating objects from input streams (e.g., files) while maintaining the factory's extensibility. The factory should support both parameterless creation and stream-based creation using integer type identifiers.

# Communication & Style Preferences
- Use C++ with modern practices
- Maintain clear separation between registration and creation logic
- Use templates and function pointers for type safety
- Provide clear error messages for unknown types

# Operational Rules & Constraints
1. Maintain TWO separate callback maps:
   - One for parameterless creation (existing CreateFigureCallback)
   - One for stream-based creation (new StreamCreateCallback)
2. Use integer type identifiers (not strings) to avoid changing existing classes
3. Each concrete class must provide BOTH:
   - A parameterless creation function
   - A stream-based creation function
4. The factory must provide:
   - RegisterFigure() for parameterless callbacks
   - RegisterStreamCreator() for stream callbacks
   - CreateFigure() for parameterless creation
   - CreateFigureFromFile() for stream-based creation
5. Stream callbacks must accept (std::istream&, int) parameters
6. All registration must happen BEFORE any creation attempts

# Anti-Patterns
- Do NOT use if-else chains or switch statements for type selection
- Do NOT hardcode type names or strings
- Do NOT mix parameterless and stream-based creation in the same callback map
- Do NOT assume registration order

# Interaction Workflow
1. Client code registers both parameterless and stream creators for each type
2. To create from file: read type ID first, then call CreateFigureFromFile(stream, id)
3. Factory looks up stream callback by ID and invokes it with the stream
4. Stream callback reads only the parameters for its specific type


Example registration:
```cpp
// Parameterless
factory.RegisterFigure(TRIANGLE, CreateTriangle);
// Stream-based
factory.RegisterStreamCreator(TRIANGLE, CreateTriangleFromStream);
```

Example usage:
```cpp
std::ifstream file("figures.txt");
int typeId;
file >> typeId;
Figure* fig = factory.CreateFigureFromFile(file, typeId);
```

## Triggers

- extend factory to support file deserialization
- implement CreateFigureFromFile with factory pattern
- add stream-based creation to factory
- factory pattern with two callback maps
