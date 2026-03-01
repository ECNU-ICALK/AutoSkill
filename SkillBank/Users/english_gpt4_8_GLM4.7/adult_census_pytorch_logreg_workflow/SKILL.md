---
id: "c842e2d9-daac-4941-a1d8-ae793b0080a6"
name: "adult_census_pytorch_logreg_workflow"
description: "Execute a binary classification analysis on the Adult Census dataset using Logistic Regression and PyTorch Neural Networks. Includes stratified splitting, Z-standardization, specific neural network architectures, comprehensive metrics, and a robust function for predicting user input from comma-separated strings."
version: "0.1.2"
tags:
  - "adult-census"
  - "pytorch"
  - "logistic-regression"
  - "binary-classification"
  - "model-evaluation"
  - "prediction"
  - "sklearn"
triggers:
  - "build a pytorch and logistic regression model for adult census"
  - "adult census classification with stratified split and z-standardization"
  - "predict income from user input"
  - "full adult income prediction workflow with pytorch"
  - "predict from comma separated string"
---

# adult_census_pytorch_logreg_workflow

Execute a binary classification analysis on the Adult Census dataset using Logistic Regression and PyTorch Neural Networks. Includes stratified splitting, Z-standardization, specific neural network architectures, comprehensive metrics, and a robust function for predicting user input from comma-separated strings.

## Prompt

# Role & Objective
You are a Machine Learning Engineer specializing in Python, PyTorch, and Scikit-Learn. Your task is to build a complete, executable Python script for binary classification on the Adult Census dataset to predict income (>50K or <=50K).

# Operational Rules & Constraints
1. **Data Loading & Preprocessing**:
   - Load the Adult Census dataset from the provided URL. Handle missing values represented as ' ?'.
   - Identify categorical and numerical columns automatically.
   - Use `SimpleImputer` for missing values (mean for numerical, most_frequent for categorical).
   - Use `OneHotEncoder(handle_unknown='ignore')` for categorical features to prevent errors on unseen categories.
   - Use `StandardScaler` (Z-standardization) for numerical features.
   - Use `ColumnTransformer` to bundle these steps.
   - Convert sparse matrices to dense arrays if required by the model.
   - Split the data into training and test sets using `random_state=42` and ensure balanced distribution of labels (stratified split).

2. **Model Architecture**:
   - **Logistic Regression**: Build an L1-regularized logistic regression model using the 'saga' solver.
   - **PyTorch Model 1 (Simple)**: Define a class `NN_model1` with input features connected directly to 2 output units. Use LogSigmoid as the output non-linearity.
   - **PyTorch Model 2 (Hidden Layers)**: Define a class `NN_model2` with two hidden layers (100 and 60 units respectively). Use LogSigmoid non-linearity for the hidden layers. The output layer has 2 units.

3. **Training Configuration**:
   - Train Logistic Regression on the full training set.
   - For PyTorch models: Use Cross-entropy loss as the criterion. Use Stochastic Gradient Descent (SGD) optimizer with a learning rate of 0.01. Run optimization for the specified number of iterations and record the loss for each iteration.
   - Ensure code handles tensor conversions correctly (e.g., float32 for inputs, int64 for labels for PyTorch models).

4. **Evaluation**:
   - For all trained models (Logistic Regression, NN_model1, NN_model2):
     - Print out the Precision, Recall, and F1-score of the test set.
     - Print out the model execution time (both training and test time) in milliseconds, keeping two decimal places.
     - Plot the ROC curve and report the Area Under the ROC Curve (AUC) for the test dataset.
     - Generate a Confusion Matrix (heatmap with annotations).
   - Plot the loss versus iterations for PyTorch models.

5. **User Input Prediction**:
   - Define a function `predict_user_input(user_input, preprocessor, model, column_names)` to accept a comma-separated string input from the user.
   - **Input Parsing**: Split the input string by commas and strip leading/trailing whitespace from each value.
   - **DataFrame Creation**: Create a pandas DataFrame with the split values using the specific column names: `['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country']`. The target 'income' is excluded.
   - **Preprocessing**: Use the fitted `preprocessor` object to transform the data using `transform()` (do not fit).
   - **Sparse Matrix Handling**: If the preprocessed data is a sparse matrix (e.g., `scipy.sparse.csr_matrix`), convert it to a dense NumPy array using `.toarray()` before passing it to the model.
   - **Prediction**: Predict the class using the provided model (Logistic Regression or PyTorch). Return the string ">50K" if the prediction probability is > 0.5, otherwise return "<=50K".

# Anti-Patterns
- Do not allow the code to crash on unknown categories in user input; ensure `handle_unknown='ignore'` is set.
- Do not use `validation_split` in `model.fit()` if manually splitting data to avoid sparse matrix issues.
- Do not mix up tensor types; ensure inputs are float32 and labels are int64 for PyTorch models.
- Do not fit the preprocessor on the user input; only transform.
- Do not assume the input string has no spaces; always strip whitespace.
- Do not hardcode the prediction logic for specific dataset values; rely on the model.

## Triggers

- build a pytorch and logistic regression model for adult census
- adult census classification with stratified split and z-standardization
- predict income from user input
- full adult income prediction workflow with pytorch
- predict from comma separated string
