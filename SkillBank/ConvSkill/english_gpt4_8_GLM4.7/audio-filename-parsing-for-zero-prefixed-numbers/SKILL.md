---
id: "b0c6f5f4-a53c-42e7-9b2f-d08c862280b0"
name: "Audio Filename Parsing for Zero-Prefixed Numbers"
description: "Parses text strings to map to audio files. If text starts with '0' followed by a digit (e.g., '01'), it splits the text into individual characters to fetch corresponding audio files. Otherwise, it uses the whole text as the filename."
version: "0.1.0"
tags:
  - "python"
  - "audio"
  - "parsing"
  - "text-processing"
  - "pydub"
triggers:
  - "parse text for audio filenames"
  - "handle zero prefixed numbers in audio"
  - "split 01 02 for audio files"
  - "audio filename generation logic"
---

# Audio Filename Parsing for Zero-Prefixed Numbers

Parses text strings to map to audio files. If text starts with '0' followed by a digit (e.g., '01'), it splits the text into individual characters to fetch corresponding audio files. Otherwise, it uses the whole text as the filename.

## Prompt

# Role & Objective
Parse text strings to determine audio filenames based on specific zero-prefix rules.

# Operational Rules & Constraints
1. Analyze the input text string, splitting it by spaces if necessary.
2. For each text token, check if it starts with '0' and is followed by another digit (e.g., "01", "02").
3. If the condition is met:
   - Iterate through each character in the text token.
   - For each character, generate a filename in the format "Audio/{character}.mp3".
4. If the condition is not met:
   - Generate a single filename using the whole text token in the format "Audio/{text}.mp3".
5. Assume the use of `AudioSegment` from pydub to combine the resulting audio segments.

# Anti-Patterns
- Do not split text that starts with '0' but is not followed by a digit.
- Do not split text that does not start with '0'.

## Triggers

- parse text for audio filenames
- handle zero prefixed numbers in audio
- split 01 02 for audio files
- audio filename generation logic
