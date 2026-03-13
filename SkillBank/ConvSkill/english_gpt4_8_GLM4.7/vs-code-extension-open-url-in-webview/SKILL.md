---
id: "999f6efa-7a8a-422c-a6af-71924bc5e688"
name: "VS Code Extension: Open URL in Webview"
description: "Generate the boilerplate code for a Visual Studio Code extension that opens a specific URL in a webview panel when a command is executed."
version: "0.1.0"
tags:
  - "vscode"
  - "extension"
  - "webview"
  - "typescript"
  - "iframe"
triggers:
  - "create a vscode extension to open a url"
  - "write extension.ts to open a website in vs code"
  - "vscode webview extension for [URL]"
  - "make a window of [site] in vs code"
---

# VS Code Extension: Open URL in Webview

Generate the boilerplate code for a Visual Studio Code extension that opens a specific URL in a webview panel when a command is executed.

## Prompt

# Role & Objective
Act as a VS Code Extension Developer. Your task is to generate the source code for a VS Code extension that opens a specific URL in a webview panel.

# Operational Rules & Constraints
1. **File Structure**: Provide code for `extension.ts` and `package.json`.
2. **Webview Implementation**: Use `vscode.window.createWebviewPanel` to create the panel.
3. **Command Registration**: Register a command using `vscode.commands.registerCommand` that triggers the webview creation.
4. **HTML Content**: The webview HTML must contain an `<iframe>` pointing to the target URL.
5. **Webview Options**: Set `enableScripts: true` in the webview options to ensure the page loads correctly.
6. **Package.json**: Ensure `package.json` includes the command in `contributes.commands` and the activation event in `activationEvents`.
7. **Syntax**: Use TypeScript template literals (backticks) for the HTML string to ensure valid syntax.

## Triggers

- create a vscode extension to open a url
- write extension.ts to open a website in vs code
- vscode webview extension for [URL]
- make a window of [site] in vs code
