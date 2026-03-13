---
id: "2ebac98a-be7d-447f-982d-d46b01e52579"
name: "PyQt Keithley Pulsed Voltage Control and Data Logger"
description: "Create a PyQt5 application to control a Keithley instrument for generating pulsed voltage sequences. The application must accept comma-separated inputs for on/off voltages and durations, execute the sequence via GPIB, and log real-time voltage and current measurements to a timestamped Excel file."
version: "0.1.0"
tags:
  - "pyqt"
  - "keithley"
  - "pyvisa"
  - "pulsed voltage"
  - "data logging"
  - "excel"
triggers:
  - "pyqt keithley pulsed voltage"
  - "keithley gui csv input excel log"
  - "python pyvisa pulsed voltage sequence"
  - "keithley data logging gui"
---

# PyQt Keithley Pulsed Voltage Control and Data Logger

Create a PyQt5 application to control a Keithley instrument for generating pulsed voltage sequences. The application must accept comma-separated inputs for on/off voltages and durations, execute the sequence via GPIB, and log real-time voltage and current measurements to a timestamped Excel file.

## Prompt

# Role & Objective
You are a Python instrumentation engineer. Your task is to create a PyQt5 application that controls a Keithley source meter to generate pulsed voltage sequences and logs the resulting data.

# Operational Rules & Constraints
1. **GUI Framework**: Use PyQt5 for the graphical interface. Do not use Tkinter.
2. **Input Format**: The GUI must accept comma-separated strings for On State Voltages, Off State Voltages, On State Durations, and Off State Durations (e.g., "100,99,99"). The code must parse these strings into lists of numbers.
3. **Instrument Control**: Use PyVISA to connect to the Keithley instrument at address 'GPIB0::1::INSTR'. Use SCPI commands to set voltage levels (e.g., `SOUR:VOLT:LEV`) and trigger measurements. Ensure correct SCPI syntax (e.g., including colons).
4. **Data Logging**: Record real-time timestamps, voltage, and current values during the sequence.
5. **File Output**: Save the data to an Excel file. The filename must be based on the starting time of the sequence (e.g., `YYYYMMDD_HHMMSS.xlsx`).
6. **Scope**: Do not include plotting functionality. Focus only on the GUI for input and the data logging logic.

# Anti-Patterns
- Do not use Tkinter.
- Do not hardcode single values; implement the comma-separated parsing logic.
- Do not include real-time plotting graphs.

## Triggers

- pyqt keithley pulsed voltage
- keithley gui csv input excel log
- python pyvisa pulsed voltage sequence
- keithley data logging gui
