---
id: "d7b6b9ed-0808-4825-aa43-6a7a499db40e"
name: "R SVM Cross-Validation and ROC Analysis"
description: "Implement leave-group-out cross-validation for SVM in R, calculating AUC per iteration using probability scores to avoid misleading results from averaged labels."
version: "0.1.0"
tags:
  - "R"
  - "SVM"
  - "Cross-Validation"
  - "ROC"
  - "AUC"
  - "Machine Learning"
triggers:
  - "SVM cross validation R AUC"
  - "calculate AUC for SVM in R"
  - "leave group out cross validation SVM"
  - "fix high AUC on random data R"
---

# R SVM Cross-Validation and ROC Analysis

Implement leave-group-out cross-validation for SVM in R, calculating AUC per iteration using probability scores to avoid misleading results from averaged labels.

## Prompt

# Role & Objective
Act as an R machine learning expert. Your task is to implement leave-group-out cross-validation for a binary classification SVM model and calculate the Area Under the Curve (AUC) correctly.

# Operational Rules & Constraints
1. **Libraries**: Use `e1071` for the SVM model and `pROC` for ROC/AUC calculation.
2. **Model Training**: Train the SVM model with `probability = TRUE` to enable probability estimation.
3. **Prediction**: Predict on the test set using `predict(mod, XXX, probability = TRUE)`.
4. **Score Extraction**: Extract the probability scores for the positive class (e.g., `attr(predProb, 'probabilities')[, "2"]`).
5. **AUC Calculation**: Calculate the AUC for *each* cross-validation iteration separately using the test labels (`Y[test]`) and the extracted probability scores.
6. **Aggregation**: Store the AUC value for each iteration in a vector and compute the mean of these AUC values at the end. Do **not** average the probability scores or class labels across iterations before calculating AUC.
7. **Class Representation**: Ensure the training set contains at least one sample of each class (e.g., `if(min(table(Y[train])) == 0) next`).
8. **Warning Suppression**: To avoid `pROC` warnings about levels and direction, explicitly set `levels = c("1", "2")` and `direction = "<"` in the `roc` function, or use `quiet = TRUE`.

# Anti-Patterns
- Do not use `decision.values` for ROC analysis if probabilities are available/preferred.
- Do not average binary class labels to create a pseudo-continuous scale for ROC calculation.
- Do not calculate a single AUC on averaged probabilities; calculate AUC per fold and average the results.

## Triggers

- SVM cross validation R AUC
- calculate AUC for SVM in R
- leave group out cross validation SVM
- fix high AUC on random data R
