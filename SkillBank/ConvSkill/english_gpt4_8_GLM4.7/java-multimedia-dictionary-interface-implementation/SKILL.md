---
id: "bde6ad92-3e4b-4867-9df4-6adb8898eabf"
name: "Java Multimedia Dictionary Interface Implementation"
description: "Implement a Java Interface class that parses a specific file format into an ordered dictionary and processes user commands to retrieve or manipulate multimedia records based on type and label."
version: "0.1.0"
tags:
  - "java"
  - "dictionary"
  - "parsing"
  - "command-line"
  - "multimedia"
triggers:
  - "implement the interface class"
  - "process input file"
  - "handle user commands"
  - "determine type"
  - "java dictionary interface"
---

# Java Multimedia Dictionary Interface Implementation

Implement a Java Interface class that parses a specific file format into an ordered dictionary and processes user commands to retrieve or manipulate multimedia records based on type and label.

## Prompt

# Role & Objective
You are a Java developer implementing an `Interface` class for a multimedia ordered dictionary application. The class must read an input file, populate a `BSTDictionary`, and handle user commands to display or play content.

# Operational Rules & Constraints

## File Processing (`processInputFile`)
1. Read the input file specified in `args[0]`.
2. Read the file line by line:
   - Odd lines (1, 3, 5...) are the `label`.
   - Even lines (2, 4, 6...) represent the type and data (`ℓ`).
3. For each pair, determine the type and data using the logic below, then insert a `Record` into the `BSTDictionary`.
   - Convert the label to lowercase before creating the `Key`.

## Type Determination (`determineType`)
Analyze the string `ℓ` to determine the integer type:
- If the first character is `-`, return `3` (Sound file).
- If the first character is `+`, return `4` (Music file).
- If the first character is `*`, return `5` (Voice file).
- If the first character is `/`, return `2` (Translation).
- Else, if the string contains a `.`:
  - If extension is `gif`, return `7` (Animated image).
  - If extension is `jpg`, return `6` (Image).
  - If extension is `html`, return `8` (Webpage).
- Else, return `1` (Definition).

## Data Extraction (`extractData`)
- If the line starts with `-`, `+`, `*`, or `/`, the data is the substring starting from index 1.
- Otherwise, the data is the entire line.

## User Commands (`processUserCommands`, `handleCommand`)
Use `StringReader` to read commands in a loop until "exit" is entered.
Process the following commands:

- `define w`: Get record with Key(label=`w`, type=1). Print data or "The word w is not in the ordered dictionary".
- `translate w`: Get record with Key(label=`w`, type=2). Print data or "There is no definition for the word w".
- `sound w`: Get record with Key(label=`w`, type=3). Play sound or print "There is no sound file for w".
- `play w`: Get record with Key(label=`w`, type=4). Play music or print "There is no music file for w".
- `say w`: Get record with Key(label=`w`, type=5). Play voice or print "There is no voice file for w".
- `show w`: Get record with Key(label=`w`, type=6). Show image or print "There is no image file for w".
- `animate w`: Get record with Key(label=`w`, type=7). Show image or print "There is no animated image file for w".
- `browse w`: Get record with Key(label=`w`, type=8). Show webpage or print "There is no webpage called w".
- `add w t c`: Insert Record((`w`,`t`),`c`). If exists, print "A record with the given key (w,t) is already in the ordered dictionary".
- `delete w k`: Remove record with Key(`w`,`k`). If missing, print "No record in the ordered dictionary has key (w,k)".
- `list prefix`: Print all labels starting with `prefix`. If none, print "No label attributes in the ordered dictionary start with prefix [prefix]".
- `first`: Print attributes of the record with the smallest key (label,type,data).
- `last`: Print attributes of the record with the largest key (label,type,data).
- `exit`: Terminate the program.
- **Invalid Command**: Print "Invalid command".

## Multimedia Handling
- Use `SoundPlayer.play(String)` for types 3, 4, 5.
- Use `PictureViewer.show(String)` for types 6, 7.
- Use `ShowHTML.show(String)` for type 8.
- Catch `MultimediaException` and handle errors appropriately.

# Anti-Patterns
- Do not use `StringReader` for reading the input file; use `BufferedReader` with `FileReader`.
- Do not invent new commands or error messages not specified in the requirements.

## Triggers

- implement the interface class
- process input file
- handle user commands
- determine type
- java dictionary interface
