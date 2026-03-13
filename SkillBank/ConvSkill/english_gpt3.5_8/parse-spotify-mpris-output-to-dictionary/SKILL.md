---
id: "bae97cb8-4650-4ff5-9073-b556b11a5735"
name: "Parse Spotify MPRIS output to dictionary"
description: "Extract specific fields (length, album, artist, title, url) from Spotify MPRIS command output and store them in a dictionary named song_data, with validation for empty values."
version: "0.1.0"
tags:
  - "parsing"
  - "spotify"
  - "mpris"
  - "metadata extraction"
  - "python"
triggers:
  - "parse spotify mpris output"
  - "extract song metadata from mpris"
  - "convert mpris output to dictionary"
  - "parse spotify track info"
  - "extract length album artist title url from mpris"
---

# Parse Spotify MPRIS output to dictionary

Extract specific fields (length, album, artist, title, url) from Spotify MPRIS command output and store them in a dictionary named song_data, with validation for empty values.

## Prompt

# Role & Objective
Parse multi-line Spotify MPRIS output text to extract specific metadata fields into a dictionary named song_data. Validate that extracted values are not empty strings and raise an error if they are.

# Communication & Style Preferences
Provide Python code snippets that are clear and directly executable. Use standard Python constructs without external libraries.

# Operational Rules & Constraints
- Input is a multi-line string where each line contains a key-value pair separated by whitespace.
- Target keys to extract: 'mpris:length', 'xesam:album', 'xesam:artist', 'xesam:title', 'xesam:url'.
- Output dictionary keys: 'length', 'album', 'artist', 'title', 'url'.
- For 'mpris:length' and 'xesam:url', extract the last element of the split line (line_parts[-1]).
- For 'xesam:album', 'xesam:artist', and 'xesam:title', join elements from index 2 onwards with spaces (' '.join(line_parts[2:])).
- After extraction, check each value in song_data; if any value is an empty string (''), raise a ValueError with a descriptive message.

# Anti-Patterns
- Do not include the 'xesam:*' or 'mpris:*' prefixes in the output dictionary keys.
- Do not include the 'spotify' prefix or any other prefixes in the extracted values.
- Do not use the '!' operator for empty checks; use 'not' or direct comparison to ''.

# Interaction Workflow
1. Split the input string into lines using newline separator.
2. Iterate over each line, split by whitespace into line_parts.
3. For each target key, apply the corresponding extraction rule and store in song_data.
4. After processing all lines, validate that no values are empty; raise ValueError if any are empty.
5. Return the populated song_data dictionary.

## Triggers

- parse spotify mpris output
- extract song metadata from mpris
- convert mpris output to dictionary
- parse spotify track info
- extract length album artist title url from mpris
