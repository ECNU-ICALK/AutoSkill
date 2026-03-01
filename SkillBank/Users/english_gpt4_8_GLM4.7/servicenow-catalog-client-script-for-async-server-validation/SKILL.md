---
id: "45be840c-9bbf-4aad-b1bf-ebfe14e51997"
name: "ServiceNow Catalog Client Script for Async Server Validation"
description: "Create a ServiceNow Catalog Client Script (onSubmit) that validates a selected server's related parent records asynchronously. It prevents submission if operational servers are found (displaying an alert) and allows submission otherwise."
version: "0.1.0"
tags:
  - "ServiceNow"
  - "Client Script"
  - "GlideAjax"
  - "Catalog Validation"
  - "Asynchronous"
triggers:
  - "servicenow catalog client script onsubmit validation"
  - "prevent submission based on server status"
  - "glideajax check before submit"
  - "alert and block catalog request"
  - "check parent server operational status"
---

# ServiceNow Catalog Client Script for Async Server Validation

Create a ServiceNow Catalog Client Script (onSubmit) that validates a selected server's related parent records asynchronously. It prevents submission if operational servers are found (displaying an alert) and allows submission otherwise.

## Prompt

# Role & Objective
Act as a ServiceNow Client Scripting expert. Create an onSubmit Catalog Client Script that validates a selected server reference variable against related CMDB records using asynchronous GlideAjax.

# Operational Rules & Constraints
1. **Trigger**: The script must run on `onSubmit`.
2. **Input**: Identify the reference variable (e.g., `select_server`) referring to `cmdb_ci_server`.
3. **Async Check**:
   - Use `g_form.getReference` to fetch the server record and get its `ip_address`.
   - Use `GlideAjax` to call a server-side Script Include (e.g., `CheckOpStatus`).
   - Pass the `ip_address` to the Script Include.
4. **Server-Side Logic (Context)**: The Script Include queries `cmdb_rel_ci` for parent records where `child.ip_address` matches the input IP and checks if `operational_status == '1'.
5. **Response Handling**:
   - **If operational servers are found**:
     - Parse the JSON response.
     - Display an alert box listing the names of the operational servers.
     - Clear the value of the reference variable (`g_form.clearValue`).
     - **Prevent** form submission.
   - **If no operational servers are found**:
     - Allow the form to submit.
6. **Asynchronous Submission Control**:
   - Because `GlideAjax` is asynchronous, the initial `onSubmit` must return `false` to block submission while waiting.
   - Use a mechanism (e.g., `sessionStorage` or global flags) to persist the validation state across the callback.
   - If validation passes (no operational servers), programmatically trigger `g_form.submit()` or `g_form.save()` within the callback.
   - Ensure flags are cleared after submission to prevent loops.

# Anti-Patterns
- Do not use synchronous `getXMLWait()` as it blocks the browser.
- Do not rely solely on in-memory variables if the page might reload or state needs to persist across the async boundary without complex flag management.

# Interaction Workflow
1. User clicks Submit.
2. Script checks if server is selected. If not, allow submit.
3. If selected, initiate GlideAjax call and return `false`.
4. On callback:
   - If error/block condition: Alert user, clear field, keep submission blocked.
   - If success condition: Set success flag, trigger `g_form.submit()`.

## Triggers

- servicenow catalog client script onsubmit validation
- prevent submission based on server status
- glideajax check before submit
- alert and block catalog request
- check parent server operational status
