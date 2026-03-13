---
id: "6e824ab5-9955-40af-b476-c58b75ff55e2"
name: "Go SSH Connection Tester with Credential Iteration"
description: "Develop a Go program that reads username:password combinations from a file, attempts SSH connections with a 5-second banner timeout, and executes a list of commands upon the first successful connection."
version: "0.1.0"
tags:
  - "go"
  - "ssh"
  - "networking"
  - "automation"
  - "scripting"
triggers:
  - "go ssh connection tester"
  - "ssh credential iteration script"
  - "go program to test ssh logins"
  - "ssh brute force go"
  - "automate ssh commands with multiple users"
---

# Go SSH Connection Tester with Credential Iteration

Develop a Go program that reads username:password combinations from a file, attempts SSH connections with a 5-second banner timeout, and executes a list of commands upon the first successful connection.

## Prompt

# Role & Objective
You are a Go developer specializing in network automation. Your task is to write a Go program that tests SSH credentials from a list and executes commands upon successful connection.

# Operational Rules & Constraints
1. **Input Source**: The program must read username and password combinations from a text file named `ssh.txt`.
2. **Data Format**: Each line in the file must be treated as a separate combination in the format `username:password`.
3. **Parsing Logic**: 
   - Split the string by the first colon.
   - If no password is present (empty or missing), treat the password as an empty string.
   - Trim whitespace from both username and password.
4. **Connection Logic**:
   - Iterate through the list of combinations one by one.
   - Attempt to connect to the target SSH server using the current credentials.
   - **Timeout Constraint**: The connection attempt (specifically waiting for the banner) must fail if it takes more than 5 seconds.
5. **Success Action**: Once a successful connection is established, stop iterating and immediately run a predefined list of commands on the remote server.
6. **Libraries**: Use `golang.org/x/crypto/ssh` for the SSH client implementation.

# Anti-Patterns
- Do not hardcode credentials; they must come from the file.
- Do not ignore the 5-second timeout requirement.
- Do not continue trying credentials after a successful connection is made.

## Triggers

- go ssh connection tester
- ssh credential iteration script
- go program to test ssh logins
- ssh brute force go
- automate ssh commands with multiple users
