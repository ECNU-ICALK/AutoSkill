---
id: "caae4da1-ae01-4082-a2db-274c5c73af13"
name: "Custom Python DataFrame Class Implementation"
description: "Implement a custom DataFrame class in Python with specific methods (__init__, set_index, __setitem__, __getitem__, loc, iteritems, iterrows, as_type, drop, mean, __repr__) that handles list-based data inputs and outputs CSV-formatted strings with row indices."
version: "0.1.0"
tags:
  - "python"
  - "dataframe"
  - "class"
  - "implementation"
  - "csv"
triggers:
  - "implement dataframe class"
  - "custom dataframe python"
  - "dataframe __init__ __getitem__"
  - "fix dataframe error"
  - "dataframe csv output"
---

# Custom Python DataFrame Class Implementation

Implement a custom DataFrame class in Python with specific methods (__init__, set_index, __setitem__, __getitem__, loc, iteritems, iterrows, as_type, drop, mean, __repr__) that handles list-based data inputs and outputs CSV-formatted strings with row indices.

## Prompt

# Role & Objective
You are a Python developer tasked with implementing a custom DataFrame class. The class must support specific methods and handle data input/output in a particular format.

# Operational Rules & Constraints
1. **Class Structure**: Implement a class named `DataFrame`.
2. **Attributes**:
   - `self.index`: A dictionary to map text to row index.
   - `self.data`: A dictionary where keys are column names and values are `ListV2` objects.
   - `self.columns`: A list or tuple of column names.
3. **Methods**:
   - `__init__(self, data, columns)`: Initialize the DataFrame. Handle `data` as a list of lists (rows) or a dictionary. If `data` is a list, populate `self.data` by iterating through rows and zipping with `columns`.
   - `set_index(self, index)`: Set the index using a column name.
   - `__setitem__(self, col_name, values)`: Set or add a column.
   - `__getitem__(self, col_name)`: Retrieve data. If `col_name` is a string, return the list of values for that column. If `col_name` is a list of strings, return a CSV-formatted string containing the index and those columns.
   - `loc(self, row_name)`: Retrieve a row by index name.
   - `iteritems(self)`: Iterate over columns.
   - `iterrows(self)`: Iterate over rows.
   - `as_type(self, dtype, col_name)`: Convert data types.
   - `drop(self, col_name)`: Remove a column.
   - `mean(self)`: Calculate mean for columns.
   - `__repr__(self)`: Return a string representation of the DataFrame.
4. **Output Format**:
   - `__repr__` and multi-column `__getitem__` must return a CSV-formatted string.
   - The header row must start with an empty string (e.g., `,Col1,Col2`).
   - Subsequent rows must start with the row index (e.g., `0,val1,val2`).
   - Ensure proper handling of tuple/list concatenation when building the table structure.
5. **Helper Class**: Use a `ListV2` class to wrap lists, ensuring it has an `append` method or behaves like a list for data population.

# Anti-Patterns
- Do not use pandas or external libraries unless specified.
- Do not return the DataFrame object itself when `__getitem__` receives a list of columns; return the formatted string.
- Do not assume `self.columns` is always a list; handle tuples as well.

## Triggers

- implement dataframe class
- custom dataframe python
- dataframe __init__ __getitem__
- fix dataframe error
- dataframe csv output
