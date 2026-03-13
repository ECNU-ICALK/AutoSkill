---
id: "d7bd81e9-2095-4fc4-9085-1dd272736b2a"
name: "Configure Pydantic BaseSettings with .env file"
description: "Configure a Pydantic BaseSettings class to load environment variables from a .env file, ensuring correct relative or absolute path resolution."
version: "0.1.0"
tags:
  - "pydantic"
  - "python"
  - "configuration"
  - "env-file"
  - "base-settings"
triggers:
  - "configure pydantic settings"
  - "pydantic env file not found"
  - "base settings env_file"
  - "pydantic validation error missing fields"
  - "where to store .env file"
---

# Configure Pydantic BaseSettings with .env file

Configure a Pydantic BaseSettings class to load environment variables from a .env file, ensuring correct relative or absolute path resolution.

## Prompt

# Role & Objective
Configure a Pydantic `BaseSettings` class to load environment variables from a `.env` file located at a specific path relative to the settings file.

# Operational Rules & Constraints
1. Define a class `Settings` inheriting from `pydantic.BaseSettings`.
2. Include fields for database configuration: `db_url` (PostgresDsn), `db_host` (str), `db_port` (int), `db_user` (str), `db_name` (str), `db_pass` (str).
3. Include fields for app configuration: `port` (int), `host` (str).
4. Configure the inner `Config` class with `env_file` set to the correct relative path (e.g., `.env` for same directory, `../.env` for parent directory).
5. Set `env_file_encoding` to "utf-8".

# Anti-Patterns
- Do not change the field names or types provided in the user's schema.
- Do not assume the `.env` file is in the system root.

## Triggers

- configure pydantic settings
- pydantic env file not found
- base settings env_file
- pydantic validation error missing fields
- where to store .env file
