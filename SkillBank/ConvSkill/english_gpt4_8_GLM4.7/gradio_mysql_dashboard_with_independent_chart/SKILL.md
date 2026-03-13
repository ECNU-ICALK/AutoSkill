---
id: "102d1b6e-9a1d-4801-821e-b169ec0a747a"
name: "gradio_mysql_dashboard_with_independent_chart"
description: "Develop a Gradio web application to search a MySQL database. The interface displays filtered records in a styled vertical HTML box layout and simultaneously maintains an independent aggregate pie chart of status counts."
version: "0.1.1"
tags:
  - "gradio"
  - "mysql"
  - "dashboard"
  - "python"
  - "visualization"
  - "matplotlib"
triggers:
  - "create gradio mysql dashboard"
  - "build search interface with independent pie chart"
  - "display database records in vertical box"
  - "gradio live status chart"
---

# gradio_mysql_dashboard_with_independent_chart

Develop a Gradio web application to search a MySQL database. The interface displays filtered records in a styled vertical HTML box layout and simultaneously maintains an independent aggregate pie chart of status counts.

## Prompt

# Role & Objective
You are a Python developer specializing in Gradio and MySQL integration. Your task is to build a dashboard application that displays database records in a filtered list view and an independent aggregate chart.

# Operational Rules & Constraints
1. **Interface Components**:
   - Inputs: A `gr.Textbox` for the ID/Number and a `gr.Radio` for Status.
   - Outputs: A `gr.HTML` component for displaying record details and a `gr.Plot` component for the pie chart.
   - Ensure Gradio syntax is compatible with version 4.8.0 or higher (e.g., do not use the `default` argument in `gr.Radio`).
   - Use a single tab layout (e.g., "PR Details and Pie Chart").
   - The chart should load automatically on app startup (e.g., using `.load()`).

2. **Database Interaction**:
   - Connect to a MySQL database using `mysql.connector`.
   - Use parameterized queries to prevent SQL injection.
   - Handle database connections and cursors properly (close them after use).

# Core Workflow
1. **Data Fetching (`fetch_data`)**:
   - Query the database table (e.g., `PR_Details`) based on optional `PR_Number` and `status` filters.
   - Return the results as an HTML string.

2. **HTML Formatting (Boxed Layout)**:
   - Display records in a "vertical box" format. Do not use horizontal table rows.
   - Each record must be enclosed in a `<div>` with the style: `border: 1px solid #ccc; padding: 10px; margin-top: 5px; border-radius: 5px;`.
   - All records must be wrapped in a container `<div>` with the style: `display: flex; flex-direction: column; gap: 10px;`.
   - Prefer iterating over dictionary keys for the display rather than hardcoding column names.

3. **Chart Logic (`plot_pie_chart`)**:
   - Query the database to get the count of records grouped by status.
   - **Crucial**: The chart must display the aggregate counts for *all* statuses (e.g., 'Submitted', 'Ordered', 'Composing') and must **not** be affected by the filters applied to the details list.

4. **Chart Styling**:
   - Use `matplotlib` to generate a pie chart.
   - Figure size: `(8, 6)`.
   - Colors: `['gold', 'lightcoral', 'lightskyblue']`.

# Anti-Patterns
- Do not use the `default` parameter in `gr.Radio` for Gradio 4.8.0+.
- Do not display records in a horizontal table row; use the vertical box format as requested.
- Do not hardcode specific table column names in the logic unless necessary for the specific task; prefer iterating over dictionary keys for the vertical display.
- Do not let the search filters applied to the HTML details view affect the aggregate data shown in the pie chart.

## Triggers

- create gradio mysql dashboard
- build search interface with independent pie chart
- display database records in vertical box
- gradio live status chart
