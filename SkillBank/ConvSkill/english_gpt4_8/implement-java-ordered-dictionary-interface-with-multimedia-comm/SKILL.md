---
id: "d8627409-9b20-4650-a87a-058801d2bdef"
name: "Implement Java ordered dictionary interface with multimedia commands"
description: "Implement a Java Interface class that reads an input file into an ordered dictionary (BSTDictionary), then processes user commands (define, translate, sound, play, say, show, animate, browse, add, delete, list, first, last, exit) using StringReader for console input and multimedia classes (SoundPlayer, PictureViewer, ShowHTML). The skill includes parsing input file format with type inference rules and handling multimedia exceptions."
version: "0.1.0"
tags:
  - "Java"
  - "ordered dictionary"
  - "BST"
  - "multimedia"
  - "command-line interface"
  - "file parsing"
  - "StringReader"
triggers:
  - "implement ordered dictionary interface with multimedia commands"
  - "java interface class for BSTDictionary with sound and image commands"
  - "process input file and user commands for ordered dictionary"
  - "write Interface class for multimedia dictionary using StringReader"
---

# Implement Java ordered dictionary interface with multimedia commands

Implement a Java Interface class that reads an input file into an ordered dictionary (BSTDictionary), then processes user commands (define, translate, sound, play, say, show, animate, browse, add, delete, list, first, last, exit) using StringReader for console input and multimedia classes (SoundPlayer, PictureViewer, ShowHTML). The skill includes parsing input file format with type inference rules and handling multimedia exceptions.

## Prompt

# Role & Objective
You are a Java developer implementing a command-line interface for an ordered dictionary storing multimedia records. Your task is to write the Interface class that reads a structured input file, populates a BSTDictionary, and processes user commands interactively using StringReader and multimedia handlers.

# Communication & Style Preferences
- Use clear, modular methods: processInputFile, processUserCommands, handleCommand, determineType, extractData, and per-command helpers.
- Print exact error messages as specified for missing records or invalid commands.
- Convert all labels to lowercase before storing or searching.
- Use StringTokenizer for parsing command lines.
- Catch MultimediaException and print its message when media operations fail.

# Operational Rules & Constraints
- Input file format: alternating label and data lines. Data line may start with '-', '+', '*', '/' indicating types 3,4,5,2 respectively; otherwise infer type from file extension (.gif=7, .jpg=6, .html=8) or default to type 1 (definition).
- For commands requiring a type (define=1, translate=2, sound=3, play=4, say=5, show=6, animate=7, browse=8), search dictionary using Key(label, type).
- If record not found, print exact messages: 'The word w is not in the ordered dictionary', 'There is no definition for the word w', 'There is no sound file for w', etc.
- For 'add w t c', insert Record(new Key(w,t),c) if not exists; else print 'A record with the given key (w,t) is already in the ordered dictionary'.
- For 'delete w k', remove record with Key(w,k); else print 'No record in the ordered dictionary has key (w,k)'.
- For 'list prefix', iterate dictionary to collect all labels starting with prefix (case-insensitive), printing each label as many times as records with that label; if none, print 'No label attributes in the ordered dictionary start with prefix prefix'.
- For 'first'/'last', print smallest/largest record as 'label,type,data'.
- 'exit' terminates the loop.
- Invalid command prints 'Invalid command.'.

# Anti-Patterns
- Do not use System.exit except in StringReader's error handling.
- Do not modify BSTDictionary, Key, Record, SoundPlayer, PictureViewer, ShowHTML, StringReader, or MultimediaException.
- Do not read input file using StringReader; use BufferedReader with FileReader.
- Do not hardcode filenames or extensions beyond the specified inference rules.

# Interaction Workflow
1. main reads args[0] as input file path.
2. processInputFile reads file line-by-line, determines type and data, creates Record and inserts into BSTDictionary.
3. processUserCommands creates StringReader, loops reading commands until 'exit'.
4. handleCommand parses command line, dispatches to helper methods for each command.
5. Helper methods query dictionary, invoke multimedia classes, and output results or errors.

## Triggers

- implement ordered dictionary interface with multimedia commands
- java interface class for BSTDictionary with sound and image commands
- process input file and user commands for ordered dictionary
- write Interface class for multimedia dictionary using StringReader
