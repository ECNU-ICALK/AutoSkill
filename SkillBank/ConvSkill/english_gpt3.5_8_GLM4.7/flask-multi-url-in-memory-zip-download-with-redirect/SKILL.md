---
id: "b20e15c6-d4cf-4f78-afe8-6e8d88b6789c"
name: "Flask Multi-URL In-Memory Zip Download with Redirect"
description: "Generates Flask code to download files from multiple URLs, zip them in memory without saving to disk, send the zip to the user, and redirect to a success page."
version: "0.1.0"
tags:
  - "flask"
  - "python"
  - "download"
  - "zip"
  - "redirect"
triggers:
  - "download multi file from multi url flask"
  - "flask zip files in memory"
  - "flask send file and redirect"
  - "flask download without temp folder"
---

# Flask Multi-URL In-Memory Zip Download with Redirect

Generates Flask code to download files from multiple URLs, zip them in memory without saving to disk, send the zip to the user, and redirect to a success page.

## Prompt

# Role & Objective
Act as a Python Flask developer. Write code to handle a file download request.

# Operational Rules & Constraints
1. Accept a list of URLs as input (e.g., via JSON).
2. Download the content from each URL.
3. Zip the downloaded files together.
4. Do not save files to a temporary folder or disk; process them in memory.
5. Use `send_file` to send the zip file to the user's PC as an attachment.
6. After sending the file, redirect the user to a success page (e.g., `success.html`).

# Anti-Patterns
- Do not use `os.makedirs` or write files to a 'temp' directory.
- Do not return `render_template` directly for the file download; use `send_file`.

## Triggers

- download multi file from multi url flask
- flask zip files in memory
- flask send file and redirect
- flask download without temp folder
