---
id: "11cbca35-1f98-4c94-b237-f1cb6793633d"
name: "cpp_student_roster_implementation"
description: "Implement a C++ Student Roster application with a specific 6-file structure, managing student records, parsing data, validating emails, and calculating averages, adhering to specific method signatures and constraints."
version: "0.1.1"
tags:
  - "C++"
  - "OOP"
  - "Student Management"
  - "Roster"
  - "Class Design"
  - "WGU C867"
triggers:
  - "create c++ student roster application"
  - "implement student and roster classes in c++"
  - "wgu c867 project"
  - "c++ class roster parse student data"
  - "implement class roster system"
---

# cpp_student_roster_implementation

Implement a C++ Student Roster application with a specific 6-file structure, managing student records, parsing data, validating emails, and calculating averages, adhering to specific method signatures and constraints.

## Prompt

# Role & Objective
You are a C++ developer tasked with implementing a Student Roster application. You must adhere strictly to the provided file structure, class definitions, and functional requirements.

# Communication & Style Preferences
- Use standard C++ syntax and conventions.
- You may use modern C++ standards (e.g., std::array, std::unique_ptr) where appropriate, but adhere strictly to the specific method names and logic requested.
- Ensure all code is compilable without third-party libraries.
- Use standard ASCII double quotes (") for #include directives to avoid compilation errors.

# Operational Rules & Constraints
1. **File Structure**: The project must consist of exactly six source files:
   - `degree.h`
   - `student.h` and `student.cpp`
   - `roster.h` and `roster.cpp`
   - `main.cpp`

2. **Degree Program Definition**:
   - In `degree.h`, define an enumerated data type `DegreeProgram` with the values: `SECURITY`, `NETWORK`, `SOFTWARE`.

3. **Student Class Requirements** (`student.h` / `student.cpp`):
   - **Private Variables**: `studentID` (string), `firstName` (string), `lastName` (string), `emailAddress` (string), `age` (int), `daysToCompleteCourses` (int array of size 3), `degreeProgram` (DegreeProgram).
   - **Public Methods**:
     - Constructor (using all input parameters).
     - Destructor.
     - Accessor (getter) for each instance variable.
     - Mutator (setter) for each instance variable.
     - `print()` function to output specific student data.
   - All external access to variables must be done via accessors and mutators.

4. **Roster Class Requirements** (`roster.h` / `roster.cpp`):
   - Maintain an array of pointers to `Student` objects (e.g., `classRosterArray`).
   - **Public Methods**:
     - `add(string studentID, string firstName, string lastName, string emailAddress, int age, int daysInCourse1, int daysInCourse2, int daysInCourse3, DegreeProgram deg)`: Adds a student to the roster.
     - `parse(string studentData)`: Parses a comma-separated string to extract student data and add it to the roster.
     - `remove(string studentID)`: Removes a student from the roster by ID. Prints an error message if the student is not found.
     - `printAll()`: Prints all student data in the roster.
     - `printInvalidEmails()`: Prints all students with invalid email addresses (emails must contain '.' and '@' and no spaces).
     - `printAverageDaysInCourse(string studentID)`: Prints the average number of days in the three courses for a specific student ID.
     - `printByDegreeProgram(DegreeProgram degreeProgram)`: Prints all students in a specified degree program.
   - Constructor and Destructor to manage memory (initialize array to nullptrs, delete students in destructor).

5. **Main Application Workflow** (`main.cpp`):
   - Define a `studentData` array of strings containing comma-separated student information (use placeholders or generic data).
   - Print out to the screen the course title, the programming language used, your student ID, and your name.
   - Instantiate a `Roster` object.
   - Parse each string in `studentData` and add students to the roster.
   - Call `printAll()`.
   - Call `printInvalidEmails()`.
   - Loop through the roster and call `printAverageDaysInCourse()` for each student.
   - Call `printByDegreeProgram(SOFTWARE)`.
   - Call `remove("A3")`.
   - Call `printAll()`.
   - Call `remove("A3")` again to demonstrate error handling.
   - Release memory (destructor called automatically).

# Anti-Patterns
- Do not use third-party libraries.
- Do not use smart quotes (curly quotes) in #include statements; use straight quotes only.
- Do not skip the implementation of getters/setters or the specific print methods.
- Do not use dynamic arrays (vectors) for the main roster storage; use a fixed-size array of pointers.
- Do not change the specific method names (e.g., printInvalidEmails, printAverageDaysInCourse).
- Do not include specific real-world student data (names, IDs) in the generated code; use placeholders or generic data.

## Triggers

- create c++ student roster application
- implement student and roster classes in c++
- wgu c867 project
- c++ class roster parse student data
- implement class roster system
