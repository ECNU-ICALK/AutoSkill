---
id: "9e13ba40-4a35-4357-b1c1-af131f7b41b9"
name: "Generate PowerShell script for mass VMotion with Storage"
description: "Creates a PowerShell script to perform mass VMotion and Storage VMotion operations in VMware vSphere, reading server lists and destination details from an input file."
version: "0.1.0"
tags:
  - "PowerShell"
  - "VMware"
  - "VMotion"
  - "Storage VMotion"
  - "PowerCLI"
  - "automation"
triggers:
  - "write PowerShell script for mass vmtion"
  - "generate script for storage vmotion"
  - "mass migrate VMs with PowerShell"
  - "automate VMotion with CSV input"
  - "PowerCLI script for bulk VM migration"
---

# Generate PowerShell script for mass VMotion with Storage

Creates a PowerShell script to perform mass VMotion and Storage VMotion operations in VMware vSphere, reading server lists and destination details from an input file.

## Prompt

# Role & Objective
Generate a PowerShell script for mass VMotion and Storage VMotion in VMware vSphere. The script must read server names and destination details from an input file and perform migrations accordingly.

# Communication & Style Preferences
- Provide clear, commented PowerShell code.
- Use VMware PowerCLI cmdlets.
- Include placeholder variables for vCenter credentials and file paths.

# Operational Rules & Constraints
- The script must connect to vCenter Server using provided credentials.
- It must read server names and destination details from an input file.
- The input file must be in CSV format with columns: ServerName, DestinationHost, DestinationDatastore.
- For each server, the script must retrieve the VM object and perform Move-VM with both Destination and Datastore parameters.
- The script must handle cases where a server is not found in vCenter inventory.
- It must report success or failure for each migration.
- The script must disconnect from vCenter Server after completion.

# Anti-Patterns
- Do not hardcode server names, host names, or datastore names in the script.
- Do not assume the input file is always present; include basic error handling.
- Do not perform migrations without checking VM existence.

# Interaction Workflow
1. Prompt for vCenter Server credentials and input file path.
2. Read and validate the CSV input file.
3. Iterate through each server entry and perform migration.
4. Output migration status for each server.
5. Disconnect from vCenter Server.

## Triggers

- write PowerShell script for mass vmtion
- generate script for storage vmotion
- mass migrate VMs with PowerShell
- automate VMotion with CSV input
- PowerCLI script for bulk VM migration
