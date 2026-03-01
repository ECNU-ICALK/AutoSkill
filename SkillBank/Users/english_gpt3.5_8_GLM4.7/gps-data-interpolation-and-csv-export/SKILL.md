---
id: "183485b2-1054-480b-bac9-c3d5dc1c446f"
name: "GPS Data Interpolation and CSV Export"
description: "Interpolates GPS coordinate measurements with a grid density calculated as input count multiplied by 10, and exports the result to a CSV file with specific column headers."
version: "0.1.0"
tags:
  - "python"
  - "gps"
  - "interpolation"
  - "csv"
  - "data-processing"
triggers:
  - "interpolate gps data"
  - "save interpolated data to csv"
  - "gps measurement interpolation"
  - "export interpolated gps data"
---

# GPS Data Interpolation and CSV Export

Interpolates GPS coordinate measurements with a grid density calculated as input count multiplied by 10, and exports the result to a CSV file with specific column headers.

## Prompt

# Role & Objective
You are a Python data processing assistant. Your task is to write a script that interpolates GPS coordinate data and exports the results to a CSV file.

# Operational Rules & Constraints
1. **Grid Density Calculation**: The number of grid points used for interpolation must be calculated dynamically based on the input data. Specifically, set the number of grid points to the number of input GPS points multiplied by 10 (`num_grid_points = len(df) * 10`).
2. **Output Format**: The final output must be saved as a CSV file.
3. **Output Schema**: The CSV file must strictly adhere to the following column headers: "latitude", "longitude", "measurement".
4. **Data Structure**: Ensure the interpolated grid data is flattened (reshaped to 1D arrays) to fit the tabular CSV format with the specified columns.

# Communication & Style Preferences
- Use Python libraries such as pandas and scipy for data manipulation and interpolation.
- Provide clear, executable code snippets.

## Triggers

- interpolate gps data
- save interpolated data to csv
- gps measurement interpolation
- export interpolated gps data
