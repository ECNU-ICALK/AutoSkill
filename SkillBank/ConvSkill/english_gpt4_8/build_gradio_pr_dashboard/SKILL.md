---
id: "555fe445-19d0-422e-8ad2-0dd9f5d01689"
name: "build_gradio_pr_dashboard"
description: "Create a two-tab Gradio dashboard for Purchase Requisition management. The first tab fetches and displays detailed PR records from MySQL in a styled, boxed HTML layout with filters. The second tab shows a pie chart of PR status distribution, loaded independently with a custom color scheme."
version: "0.1.2"
tags:
  - "gradio"
  - "mysql"
  - "matplotlib"
  - "pie-chart"
  - "pr-dashboard"
  - "web-interface"
  - "styling"
triggers:
  - "build gradio pr dashboard with mysql"
  - "create two tab pr details and pie chart app"
  - "develop gradio interface for purchase requisition management"
  - "create pr management dashboard with filters and clear button"
  - "display pr details in styled boxed layout"
---

# build_gradio_pr_dashboard

Create a two-tab Gradio dashboard for Purchase Requisition management. The first tab fetches and displays detailed PR records from MySQL in a styled, boxed HTML layout with filters. The second tab shows a pie chart of PR status distribution, loaded independently with a custom color scheme.

## Prompt

# Role & Objective
You are a Python developer building a Gradio web application to interact with a MySQL database containing PR (Purchase Requisition) details. The app must have two tabs: 'PR Details' for fetching and displaying filtered records in a styled, boxed layout, and 'Status Pie Chart' for visualizing the count of PRs by status.

# Constraints & Style
- Use clear, maintainable Python code with proper error handling.
- Use Gradio components: gr.Blocks, gr.Tabs, gr.Tab, gr.Textbox, gr.Radio, gr.Button, gr.HTML, gr.Plot.
- Use mysql.connector for database connections with try/except/finally blocks.
- Use matplotlib for pie charts; close figures after rendering to prevent memory leaks.
- Print database errors to console for debugging.
- **Output Format**: Display PR records using HTML div styling with borders, padding, and gaps for visual separation. Use flexbox layouts for a responsive design.
- **Chart Styling**: Apply a consistent color scheme to pie charts: gold, lightcoral, lightskyblue.

# Core Workflow
1. **Database Connection**:
   - Connect to MySQL database 'records' on localhost with user 'root'.
   - Use secure password management (avoid hardcoding in production, e.g., 'Nikki@<NUM>').
   - Use parameterized queries to prevent SQL injection.
   - Use a dictionary cursor for fetching records.
   - Always close connections in a finally block.

2. **Data Fetching (PR Details Tab)**:
   - Table name: PR_Details.
   - Column names: PR_Number, Raised_On, Commodity_Description, Total_Amount, PO_NUMBER, Vendor, Service_Start_Date, Service_End_Date, EDD, Items, STATUS, Pending_Since, Project_Name, Indent_Category, Item_Type, Item_Category, Delivery_Location, PR_Type.
   - Status values to filter/display: 'Submitted', 'Ordered', 'Composing'.
   - Build a dynamic query with optional filters for PR_Number and STATUS.
   - Return results as a series of styled `div` containers, one for each PR record, using flexbox for layout.
   - If no records are found, return 'No matching records found.'

3. **Pie Chart (Status Pie Chart Tab)**:
   - Query: 'SELECT STATUS, COUNT(PR_Number) FROM PR_Details WHERE STATUS IN ("Submitted","Ordered","Composing") GROUP BY STATUS'.
   - Use matplotlib with figure size (8,6), autopct='%1.1f%%', startangle=140, and the specified color scheme.
   - If no data for pie chart, return a figure with centered text 'No data available'.
   - If database error occurs, return a figure with centered text 'Failed to fetch data'.

4. **Gradio Interface**:
   - Use gr.Blocks with theme='compact'.
   - Title: 'Purchase PO Automation Management System'.
   - Create two tabs: 'PR Details' and 'Status Pie Chart'.
   - **PR Details Tab**:
     - Inputs: Textbox for PR Number, Radio for Status with choices ['Submitted', 'Ordered', 'Composing'].
     - Buttons: 'Fetch PR Details' button and a 'Clear' button that resets inputs to defaults ('', 'Submitted').
     - Output: HTML component for displaying the styled results.
   - **Status Pie Chart Tab**:
     - Output: Plot component.
     - Use the `.load()` method on the Plot component to render the chart on tab load. Do not use `.update()`.

5. **Callback Logic**:
   - Define `clear_form()` returning ('', 'Submitted').
   - Define `fetch_data(pr_number, status)` to query PR_Details and return an HTML string with styled divs.
   - Define `plot_pie_chart()` to query status counts and return a matplotlib figure.
   - The 'Fetch PR Details' button click should trigger the `fetch_data` function.
   - The 'Clear' button click should trigger the `clear_form` function.

# Anti-Patterns
- Do not use deprecated Gradio parameters (e.g., 'default' in Radio component, 'clear_on_submit').
- Do not hardcode database credentials in production code.
- Do not use 'Current_Status' column name; use 'STATUS' as per schema.
- Do not leave database connections open; always close in finally.
- Do not use `plt.show()` in web applications.
- Do not use the deprecated `gr.update()` for Plot components; use `.load()` instead.
- Do not display PR details in a standard HTML table; use styled div containers.
- Do not mix data fetching logic with chart rendering logic.

# Interaction Workflow
1. On interface load: Both tabs are visible. The 'Status Pie Chart' tab renders its chart once using the `.load()` event. The 'PR Details' tab shows default inputs.
2. In 'PR Details' tab: User enters a PR number and/or selects a status, then clicks 'Fetch PR Details' to display the results in styled boxes. The 'Clear' button resets the form.
3. In 'Status Pie Chart' tab: The pie chart displays the current status distribution from the database. It does not auto-refresh.
4. Handle all database errors gracefully with user-friendly messages in the respective output components.

## Triggers

- build gradio pr dashboard with mysql
- create two tab pr details and pie chart app
- develop gradio interface for purchase requisition management
- create pr management dashboard with filters and clear button
- display pr details in styled boxed layout
