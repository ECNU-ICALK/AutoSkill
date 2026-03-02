---
id: "0384b604-49d2-49ed-ad90-19788044a870"
name: "selenium_automation_workflow_generator"
description: "Generates advanced Python Selenium scripts for comprehensive web automation, including navigation, JavaScript execution, dynamic content stabilization, alert/consent handling, interactive loops, and headless mode."
version: "0.1.2"
tags:
  - "selenium"
  - "web automation"
  - "python"
  - "dynamic content"
  - "javascript execution"
  - "headless browser"
triggers:
  - "write a selenium script to automate"
  - "selenium script to interact with chatbot and wait for response"
  - "generate selenium code to execute javascript"
  - "create a headless selenium script to extract data"
  - "automate web form submission and response extraction"
---

# selenium_automation_workflow_generator

Generates advanced Python Selenium scripts for comprehensive web automation, including navigation, JavaScript execution, dynamic content stabilization, alert/consent handling, interactive loops, and headless mode.

## Prompt

# Role & Objective
Generate a Python Selenium script that automates complex web interactions. The script should handle navigation, JavaScript execution, element interaction, alerts, consent dialogs, user input loops, and the extraction of dynamic content after it stabilizes.

# Constraints & Style
- Output complete, runnable Python code snippets with comments to explain key steps, especially for complex logic.
- Use clear variable names.
- Use explicit waits (WebDriverWait) with reasonable timeouts (e.g., 10 seconds) for element presence and clickability.
- For dynamic content, implement a stabilization check (e.g., wait for an element's text to be unchanged for 3 seconds) instead of a fixed wait.
- Prefer CSS selectors for element targeting.
- Include necessary imports: selenium.webdriver, By, WebDriverWait, expected_conditions, Options, and Alert.
- If user input is required, use input() to prompt the user.

# Core Workflow
1. **Initialization**: Initialize WebDriver (Chrome by default). Configure ChromeOptions with --headless and --disable-gpu if headless mode is requested. Pass options to the driver.
2. **Navigation**: Navigate to the specified URL using driver.get('<URL>').
3. **JavaScript Execution**: Use driver.execute_script('...') to execute JavaScript commands, such as clicking elements via document.querySelector() or document.getElementById().
4. **Element Interaction & Waiting**: To interact with an element, use WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'selector'))) before performing actions like send_keys() or click().
5. **Consent & Alert Handling**: If a consent dialog or alert is expected, locate and click the trigger button. Then, wait for alert_is_present() and accept it using Alert(driver).accept().
6. **Interactive Loop**: If a continuous interaction is required (e.g., a chatbot), implement a loop (e.g., `while True`) that:
   a. Prompts the user for input using `input()`. Exit the loop if the user enters an exit command like 'exit'.
   b. Locates the input element and sends the user's text.
   c. Locates and clicks the submission button.
7. **Dynamic Content Extraction**: After an action that triggers a response, implement a stabilization check:
   a. Identify the target element for the dynamic content.
   b. In a loop, retrieve the element's text.
   c. Wait for a short interval (e.g., 0.5 seconds).
   d. If the text has not changed after a defined period (e.g., 3 seconds), consider it stable.
   e. Print or return the stable content.
8. **Cleanup**: Always close the driver with driver.quit() at the end of the script, ensuring it is outside any main interaction loops.

# Anti-Patterns
- Do not use time.sleep() for waiting for elements or dynamic content; use explicit waits or change detection logic. Use time.sleep() only for fixed, non-critical pauses if absolutely necessary.
- Do not hardcode prompts, URLs, or element IDs; use placeholders like <URL> and 'element-id', or use input() for user-provided values.
- Do not assume the presence of alerts or elements without explicit wait conditions.
- Do not include print statements for debugging unless explicitly requested for output.
- Do not mix unrelated tasks in the same script.

## Triggers

- write a selenium script to automate
- selenium script to interact with chatbot and wait for response
- generate selenium code to execute javascript
- create a headless selenium script to extract data
- automate web form submission and response extraction
