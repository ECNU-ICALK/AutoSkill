---
id: "bafae059-3389-472a-ad7b-dab19d287f28"
name: "Generate Ansible task to check Node Manager ports with dynamic SSH password resolution"
description: "Creates an Ansible task that checks listening Node Manager ports on multiple hosts using netstat, with dynamic SSH password lookup from a secret file and fallback to a default password."
version: "0.1.0"
tags:
  - "ansible"
  - "port-check"
  - "netstat"
  - "dynamic-password"
  - "delegate"
triggers:
  - "check node manager port"
  - "ansible task to check listening ports"
  - "dynamic ssh password from secret"
  - "port check with delegate_to"
  - "netstat port check ansible"
---

# Generate Ansible task to check Node Manager ports with dynamic SSH password resolution

Creates an Ansible task that checks listening Node Manager ports on multiple hosts using netstat, with dynamic SSH password lookup from a secret file and fallback to a default password.

## Prompt

# Role & Objective
Generate an Ansible task that checks if Node Manager ports are listening on a set of unique IP addresses. The task must dynamically resolve SSH passwords from a secret file using a constructed variable name, with a fallback to a default password if the specific password is not found.

# Communication & Style Preferences
- Output the task in valid Ansible YAML format.
- Use clear, descriptive task names.
- Include comments only if necessary for clarity.

# Operational Rules & Constraints
- Use the shell command: 'netstat -an | grep ":{{ item.value }} " | grep LISTEN'.
- Use delegate_to to run the command on the target IP ({{ item.key }}).
- Loop over the dictionary ip_to_nm_port converted to items ({{ ip_to_nm_port | dict2items }}).
- Use the dictionary matching_hosts to map IPs to hostnames.
- Resolve the SSH password dynamically:
  - Construct the variable name as {{ hostname }}_ssh_pass where hostname is the first element of matching_hosts[item.key].
  - Use lookup('vars', constructed_var_name, default=default_ssh_pass) to retrieve the actual password from the included secret file.
  - Ensure default_ssh_pass is defined and used as a fallback.
- Include conditions to run the task only when:
  - matching_hosts is defined.
  - The current IP (item.key) exists in matching_hosts.
  - There is at least one host associated with the IP (matching_hosts[item.key] | length > 0).
- Register the task results in nm_port_checks.
- Tag the task with 'always'.

# Anti-Patterns
- Do not hardcode any IP addresses, hostnames, or port numbers in the task.
- Do not skip checking for the existence of matching_hosts or the constructed password variable.
- Do not use raw passwords; always resolve via lookup with a default fallback.

# Interaction Workflow
None required; generate the task directly based on the provided inputs.

## Triggers

- check node manager port
- ansible task to check listening ports
- dynamic ssh password from secret
- port check with delegate_to
- netstat port check ansible
