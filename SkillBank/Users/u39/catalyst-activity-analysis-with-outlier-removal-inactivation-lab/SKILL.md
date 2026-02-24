---
id: "b79864c2-4b0e-4622-90ed-4e55615da04b"
name: "catalyst-activity-analysis-with-outlier-removal-inactivation-labeling-and-control-anchoring"
description: "Automates catalyst activity analysis from CSV: computes per-sample mean conversion or degradation rate after 3-sigma outlier removal within each group, anchors 'Control' (case-insensitively detected) at the first bar position with distinct gray styling, sorts remaining samples by descending mean activity, generates a publication-ready bar chart with Chinese/English label support, and annotates samples with mean <5% as 'INACTIVATION ZONE'. Supports catalytic conversion and photocatalytic degradation data."
version: "0.1.2"
tags:
  - "catalyst"
  - "photocatalysis"
  - "activity-rate"
  - "outlier-removal"
  - "data-visualization"
  - "control-group"
triggers:
  - "催化剂转化率分析剔除离群值并标注失活区"
  - "光催化降解数据计算平均值、排序并固定对照组"
  - "plot catalyst activity bar chart with 3-sigma filter control anchoring and inactivation zone"
  - "标注失活区且对照组置顶的催化剂活性图"
  - "bar chart sorted by activity rate with control anchored and inactivation labeling"
---

# catalyst-activity-analysis-with-outlier-removal-inactivation-labeling-and-control-anchoring

Automates catalyst activity analysis from CSV: computes per-sample mean conversion or degradation rate after 3-sigma outlier removal within each group, anchors 'Control' (case-insensitively detected) at the first bar position with distinct gray styling, sorts remaining samples by descending mean activity, generates a publication-ready bar chart with Chinese/English label support, and annotates samples with mean <5% as 'INACTIVATION ZONE'. Supports catalytic conversion and photocatalytic degradation data.

## Prompt

# Goal
Given a CSV file containing catalyst screening or photocatalytic degradation data with sample/group identifiers and numeric activity measurements (e.g., conversion, degradation, removal rate in %), compute the mean activity per sample/group after removing outliers (values outside [μ−3σ, μ+3σ] *within each group*), then generate a labeled bar chart where: (1) the 'Control' sample (detected case-insensitively via 'control', 'ctrl', '对照', '空白') is fixed at position 0 with gray fill (#808080); (2) all other samples are sorted descending by their cleaned mean activity; and (3) samples with final mean activity <5% are visually and semantically flagged as 'INACTIVATION ZONE'.

# Constraints & Style
- Must perform outlier removal **per sample/group**, not globally: for each group, compute mean and std of its activity values, then retain only values satisfying |x − mean| ≤ 3×std.
- Must explicitly flag samples with final mean activity <5%: include 'inactivation_flag' (True/False) in output table; visually distinguish bars (e.g., red dashed line at y=5%, centered 'INACTIVATION ZONE' text) and annotate bars accordingly.
- Preserve robust column auto-detection: identify grouping column via keywords ('sample', 'catalyst', 'sample_id', 'group', 'sample'); identify activity column via case-insensitive keywords ('conversion', 'degradation', 'removal', 'rate', '降解', '转化', '%').
- Output table must include columns: 'group', 'mean_activity_rate' (rounded to 0.01), 'inactivation_flag'; print summary table and saved file path.
- Plot requirements: vertical bar chart; x-axis = group IDs (rotated 30°, right-aligned); y-axis = 'Activity Rate (%)', starts at 0; grid enabled; 'Control' bar color = #808080, non-Control bars use viridis colormap scaled to count; value labels on bars (2 decimals); font supporting Chinese (e.g., SimHei/Noto Sans CJK); high-res PNG (300 DPI); filename '<input_basename>.png'; top padding reserved for 'INACTIVATION ZONE' annotation.
- Drop rows with NaN in grouping or activity columns; require ≥3 non-NaN values per group to apply 3-sigma; no imputation.
- 'Control' must be excluded from sorting logic and placed first; non-Control samples sorted strictly descending by mean activity.
- Code must be self-contained, import-only, and runnable in Python 3.9+ with pandas, numpy, matplotlib, seaborn.

# Workflow
1. Load CSV and auto-identify grouping and activity columns using UTF-8/GBK auto-encoding fallback.
2. Validate data: ensure ≥1 group and ≥3 non-NaN activity values per group.
3. For each group:
   a. Compute mean (μ) and std (σ) of activity values;
   b. Filter to retain only values in [μ−3σ, μ+3σ];
   c. Recompute mean from cleaned values (rounded to 0.01).
4. Separate 'Control' row(s) (case-insensitive match on grouping column) from other samples.
5. Sort non-Control samples descending by 'mean_activity_rate'.
6. Concatenate: [Control] + [sorted non-Control] to form final order.
7. Build summary DataFrame with 'group', 'mean_activity_rate', and 'inactivation_flag'.
8. Generate and save annotated bar chart with inactivation-aware styling, control anchoring, and labeling.
9. Print summary table (ordered as visualized) and output file path.

## Triggers

- 催化剂转化率分析剔除离群值并标注失活区
- 光催化降解数据计算平均值、排序并固定对照组
- plot catalyst activity bar chart with 3-sigma filter control anchoring and inactivation zone
- 标注失活区且对照组置顶的催化剂活性图
- bar chart sorted by activity rate with control anchored and inactivation labeling
