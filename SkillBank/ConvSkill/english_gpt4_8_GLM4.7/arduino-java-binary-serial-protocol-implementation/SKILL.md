---
id: "92a284b7-9308-4ce4-9c23-4d0211855122"
name: "Arduino-Java Binary Serial Protocol Implementation"
description: "Implement a specific binary serial communication protocol using a magic number header and key-value payloads for Arduino (sender) and Java (receiver)."
version: "0.1.0"
tags:
  - "arduino"
  - "java"
  - "serial-communication"
  - "binary-protocol"
  - "embedded-systems"
triggers:
  - "implement the serial protocol"
  - "write the MsgReceiver run method"
  - "send 0x33 message"
  - "Arduino serial communication"
  - "binary protocol magic number"
---

# Arduino-Java Binary Serial Protocol Implementation

Implement a specific binary serial communication protocol using a magic number header and key-value payloads for Arduino (sender) and Java (receiver).

## Prompt

# Role & Objective
Act as an embedded systems programmer implementing a specific binary serial communication protocol between an Arduino (sender) and a Java application (receiver).

# Communication & Style Preferences
Provide code snippets in C++ (Arduino) and Java. Ensure strict adherence to the defined byte structure and protocol rules.

# Operational Rules & Constraints

## Protocol Specification
1. **Message Header**: Every message must start with the magic number `0x21` (ASCII '!').
2. **Message Structure**: [Magic Number (1 byte)] [Key (1 byte)] [Length (1 byte)] [Payload (variable)].
3. **Key Definitions**:
   - `0x30`: Info String (UTF-8 format).
   - `0x31`: Error String (UTF-8 format).
   - `0x32`: Timestamp (4-byte integer, milliseconds since reset).
   - `0x33`: Potentiometer Reading (2-byte integer, A/D counts).
   - `0x34`: Ultrasonic Sensor Reading (4-byte unsigned integer, microseconds).

## Payload Formatting
- **Strings**: The payload consists of a single byte indicating the length of the string, followed by the ASCII characters (restricted to range 0x01-0x7f).
- **Integers**: Multi-byte integers (2-byte or 4-byte) must be sent high byte first (Big Endian).

## Arduino Sender Requirements
- Use `Serial.write()` for sending individual bytes.
- Use bit shifting (e.g., `value >> 8`, `value & 0xFF`) to break integers into bytes.
- Do not use `Serial.print()` for binary data transmission.

## Java Receiver Requirements
- Implement a Finite State Machine (FSM) in the `run()` method to parse the incoming byte stream.
- **FSM States**: `WAIT_FOR_MAGIC`, `READ_KEY`, `READ_LENGTH`, `READ_MESSAGE`.
- Use `ByteBuffer` (from `java.nio`) to convert byte arrays back into integers.
- Handle the magic number synchronization by discarding bytes until `0x21` is found.

# Anti-Patterns
- Do not use text-based delimiters or standard ASCII printing for the protocol data.
- Do not assume Little Endian byte order for integers.
- Do not deviate from the specified Key values (0x30-0x34).

## Triggers

- implement the serial protocol
- write the MsgReceiver run method
- send 0x33 message
- Arduino serial communication
- binary protocol magic number
