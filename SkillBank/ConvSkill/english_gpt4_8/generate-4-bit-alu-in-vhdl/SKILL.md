---
id: "7e635636-2c02-4a08-86c8-64ef5eeebcaa"
name: "Generate 4-bit ALU in VHDL"
description: "Generates VHDL code for a 4-bit Arithmetic Logic Unit (ALU) with addition, subtraction, AND, OR, NOT operations and an unsupported flag, based on a specified entity and architecture structure."
version: "0.1.0"
tags:
  - "VHDL"
  - "ALU"
  - "4-bit"
  - "hardware"
  - "digital design"
triggers:
  - "generate a 4-bit ALU in VHDL"
  - "write VHDL code for a 4-bit ALU"
  - "create a 4-bit arithmetic logic unit in VHDL"
  - "VHDL 4-bit ALU with operations"
  - "4-bit ALU VHDL code"
---

# Generate 4-bit ALU in VHDL

Generates VHDL code for a 4-bit Arithmetic Logic Unit (ALU) with addition, subtraction, AND, OR, NOT operations and an unsupported flag, based on a specified entity and architecture structure.

## Prompt

# Role & Objective
Generate VHDL code for a 4-bit ALU as per the user-provided structure and operations.

# Communication & Style Preferences
- Output only the VHDL code without explanations.
- Use the exact libraries, entity name, port names, and architecture as specified.

# Operational Rules & Constraints
1. Use the following libraries: IEEE.STD_LOGIC_1164.ALL, IEEE.STD_LOGIC_ARITH.ALL, IEEE.STD_LOGIC_UNSIGNED.ALL.
2. Entity name must be ALU_4bit.
3. Ports:
   - operation: in std_logic_vector(2 downto 0)
   - a: in std_logic_vector(3 downto 0)
   - b: in std_logic_vector(3 downto 0)
   - result: out std_logic_vector(3 downto 0)
   - unsupported: out std_logic
4. Architecture name: Behavioral.
5. Process sensitivity list: operation, a, b.
6. Inside the process, declare a variable temp_result of type std_logic_vector(3 downto 0).
7. Use a case statement on operation:
   - "000": temp_result := std_logic_vector(unsigned(a) + unsigned(b));
   - "001": temp_result := std_logic_vector(unsigned(a) - unsigned(b));
   - "010": temp_result := a and b;
   - "011": temp_result := a or b;
   - "100": temp_result := not a;
   - others: unsupported <= '1';
8. After the case, if operation is not "100", assign result <= temp_result;.

# Anti-Patterns
- Do not add any additional operations, ports, or signals.
- Do not change the library usage or entity/architecture names.
- Do not include any testbench or simulation code.

# Interaction Workflow
None: Generate the entire VHDL code in one response.

## Triggers

- generate a 4-bit ALU in VHDL
- write VHDL code for a 4-bit ALU
- create a 4-bit arithmetic logic unit in VHDL
- VHDL 4-bit ALU with operations
- 4-bit ALU VHDL code
