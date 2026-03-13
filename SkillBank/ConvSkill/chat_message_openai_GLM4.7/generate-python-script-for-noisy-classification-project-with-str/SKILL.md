---
id: "624c1bff-d88b-4ac5-a997-5b3eff4e88a1"
name: "Generate Python script for noisy classification project with stress test"
description: "Generates a complete, runnable Python script for a machine learning project involving data loading, preprocessing, model training (KNN, LDA, QDA, RF), noise stress testing, and visualization with specific formatting (Times New Roman, bold labels, legend in upper left)."
version: "0.1.0"
tags:
  - "python"
  - "machine learning"
  - "data preprocessing"
  - "visualization"
  - "matplotlib"
triggers:
  - "generate python code for noisy classification"
  - "create ml script"
  - "complete project code"
  - "python script for stress test"
---

# Generate Python script for noisy classification project with stress test

Generates a complete, runnable Python script for a machine learning project involving data loading, preprocessing, model training (KNN, LDA, QDA, RF), noise stress testing, and visualization with specific formatting (Times New Roman, bold labels, legend in upper left).

## Prompt

You are an expert Python developer. Generate a complete, runnable Python script based on the following requirements:

1. Load data from 'train_features.npy', 'train_label.npy', 'noised_test_features.npy'.
2. Perform stratified train/validation split (80/20).
3. Preprocess data using StandardScaler and PCA (60 components).
4. Train the following models: KNN (k=9, weights='distance'), LDA, QDA, Random Forest (n_estimators=200).
5. Perform a Noise Stress Test on the validation set:
   - Add Gaussian noise to validation features at varying levels (e.g., [0.0, 0.01, ..., 0.15]).
   - Evaluate the fixed trained models on the noised validation data.
   - Repeat the noise addition 5 times for each level to get mean and std.
6. Generate a bar chart (error bars) showing Validation Accuracy vs. Noise Level for each model.
   - Plotting requirements: Font family 'Times New Roman', bold axis labels, legend in the upper left corner.
7. Save test predictions to CSV files (ID, label).

Ensure the code is modular, well-commented, and handles missing files gracefully.

## Triggers

- generate python code for noisy classification
- create ml script
- complete project code
- python script for stress test
