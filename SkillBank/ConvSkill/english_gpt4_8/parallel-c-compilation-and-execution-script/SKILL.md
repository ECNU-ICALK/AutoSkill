---
id: "27910818-a35e-468f-a85a-5e28137e27ed"
name: "Parallel C++ Compilation and Execution Script"
description: "Automates the compilation of a C++ project by compiling source files in parallel, waiting for object files, linking them into an executable, cleaning object files, and running the executable."
version: "0.1.0"
tags:
  - "C++"
  - "compilation"
  - "parallel"
  - "build"
  - "script"
triggers:
  - "compile my C++ project in parallel"
  - "generate a compilation script for C++"
  - "automate C++ build with parallel compilation"
  - "parallel compile C++ sources"
  - "C++ parallel build script"
---

# Parallel C++ Compilation and Execution Script

Automates the compilation of a C++ project by compiling source files in parallel, waiting for object files, linking them into an executable, cleaning object files, and running the executable.

## Prompt

# Role & Objective
Generate and execute a shell script to compile a C++ project in parallel, wait for all object files to be created, link them into an executable, clean up object files, and run the executable. The script should use the specified compiler, C++ standard, library, and optimization flags.

# Communication & Style Preferences
- Use clear and concise shell scripting syntax.
- Provide informative messages for each step (compilation, linking, cleanup, execution).
- Use background processes for parallel compilation and wait for completion.

# Operational Rules & Constraints
- The script must define variables for COMPILER, STANDARD, LIB, OPTIMISATION.
- Compile each source file in the background using the defined flags and output object files to the specified directory.
- After launching all compilation jobs, wait for all to complete.
- If any compilation fails, report an error and exit without linking.
- On successful compilation, link all object files into the executable with the same flags.
- Remove all object files after successful linking.
- Execute the resulting executable.

# Anti-Patterns
- Do not use polling loops to wait for object files; use the `wait` command.
- Do not proceed to linking if any compilation job fails.
- Do not leave object files after successful linking.

# Interaction Workflow
1. Define compilation variables (COMPILER, STANDARD, LIB, OPTIMISATION).
2. Compile each source file in parallel to the output directory.
3. Wait for all compilation jobs to finish.
4. Check compilation status; if any failed, exit with error.
5. Link all object files into the executable.
6. Clean up object files.
7. Run the executable.

## Triggers

- compile my C++ project in parallel
- generate a compilation script for C++
- automate C++ build with parallel compilation
- parallel compile C++ sources
- C++ parallel build script
