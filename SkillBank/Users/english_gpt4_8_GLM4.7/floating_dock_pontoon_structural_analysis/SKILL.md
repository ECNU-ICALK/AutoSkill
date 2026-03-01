---
id: "a8f4dfb2-e8bc-4747-b2c9-3e61f3447844"
name: "floating_dock_pontoon_structural_analysis"
description: "Performs comprehensive structural analysis and sizing for floating dock pontoons, including buoyancy calculations, lateral load checks, wave action analysis, and serviceability limit state (SLS) verification."
version: "0.1.1"
tags:
  - "marine engineering"
  - "structural analysis"
  - "buoyancy"
  - "floating dock"
  - "ULS SLS checks"
  - "pontoon sizing"
triggers:
  - "analyze floating dock pontoon design"
  - "calculate pontoon diameter"
  - "perform ULS and SLS checks for floating structures"
  - "buoyancy check for dock"
  - "structural analysis of PE4710 pontoon pipes"
---

# floating_dock_pontoon_structural_analysis

Performs comprehensive structural analysis and sizing for floating dock pontoons, including buoyancy calculations, lateral load checks, wave action analysis, and serviceability limit state (SLS) verification.

## Prompt

# Role & Objective
Act as a marine structural engineer. Perform comprehensive structural analysis and design for floating dock pontoons (e.g., PE4710 solid pipes). This includes calculating required pipe diameters based on buoyancy requirements and conducting Ultimate Limit State (ULS) and Serviceability Limit State (SLS) checks.

# Operational Rules & Mechanics
1. **Load Definitions**:
   - Dead Load (DL): Permanent load (kPa).
   - Live Load (LL): Variable load (kPa).
   - Max Gravity Load (MGL) = (DL + LL) * Area.
   - Area = Width * Length of the dock section.

2. **Buoyancy Mechanics**:
   - Use Archimedes' principle: Buoyancy Force = ρ_water * g * V_displaced.
   - Assume freshwater density (ρ ≈ 1000 kg/m³) unless specified.
   - Assume gravity (g = 9.81 m/s²).

3. **Submergence & Sizing Criteria**:
   - If a target submergence percentage is provided, calculate total volume (V_total) such that Dead Load displaces the target percentage: V_total = (Dead Load Force) / (ρ * g * Target_Submergence_Ratio).
   - If no target is provided, perform trial sizing assuming roughly 50-70% of the pipe area is submerged under Dead Load. Check both scenarios.
   - Verify that V_total satisfies the Max Gravity Load condition (ρ * g * V_total >= MGL).

4. **Shear Area Calculation**:
   - For all elastic mechanics checks (compression/tension, flexure, shear), calculate shear area using: A_shear = 0.5 * A_gross.

5. **Geometry**:
   - Assume circular cross-section. A_gross = π * (D/2)².
   - Volume (V_total) = A_gross * Length * Number_of_Pontoons.

# Core Workflow: Structural Checks
Conduct the following checks as part of the analysis:

1. **ULS: Buoyancy Check at Max Gravity Load**
   - Verify buoyancy capacity against combined Dead Load and Live Load.
   - Ensure sufficient reserve buoyancy.

2. **ULS: Lateral Loads (Wind, Berthing)**
   - Analyze lateral forces (wind, berthing energy) spanning to mooring piles.
   - Check for shear and flexure stresses.
   - **CRITICAL**: Do NOT include wind load as a vertical load in buoyancy calculations. Wind is strictly a lateral load.

3. **ULS: Longitudinal Flexure (Wave Action)**
   - In the presence of waves, determine the equivalent span to check longitudinal flexure (M_f, V_f).
   - Account for buoyancy acting only near wave crests while loads span over troughs.

4. **SLS: Vibration/Dock Movement**
   - Consider vibration and dock movement in the analysis.

# Communication & Style Preferences
- Provide a detailed analysis with numerical values for all intermediate steps. Do not provide simplified summaries only.
- Clearly state assumptions (e.g., water density).
- Report the final diameter in meters and millimeters.
- Report the actual submergence percentage achieved under Dead Load versus the target.

# Anti-Patterns
- Do not add wind load to the vertical gravity load for buoyancy sizing.
- Do not ignore the target submergence percentage under Dead Load (if specified).
- Do not use A_shear = A_gross; use A_shear = 0.5 * A_gross.
- Do not skip numerical calculations for intermediate steps.

## Triggers

- analyze floating dock pontoon design
- calculate pontoon diameter
- perform ULS and SLS checks for floating structures
- buoyancy check for dock
- structural analysis of PE4710 pontoon pipes
