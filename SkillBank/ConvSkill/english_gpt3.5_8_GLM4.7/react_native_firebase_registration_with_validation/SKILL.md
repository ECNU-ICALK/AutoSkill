---
id: "1d3ab876-1a2c-4569-a300-81503028531e"
name: "react_native_firebase_registration_with_validation"
description: "Generates a React Native function for user registration using Firebase Authentication and Realtime Database. It validates input fields (checking for empty values and password confirmation), creates the user account, and saves profile details (name, surname, email, phone) to the database."
version: "0.1.1"
tags:
  - "react-native"
  - "firebase"
  - "authentication"
  - "registration"
  - "validation"
  - "realtime-database"
triggers:
  - "write firebase registration function"
  - "react native firebase registration with extra fields"
  - "register user with name surname phone firebase"
  - "react native register user with validation"
  - "firebase auth and database registration"
---

# react_native_firebase_registration_with_validation

Generates a React Native function for user registration using Firebase Authentication and Realtime Database. It validates input fields (checking for empty values and password confirmation), creates the user account, and saves profile details (name, surname, email, phone) to the database.

## Prompt

# Role & Objective
You are a React Native developer. Write a `handleRegistration` function to register a user using Firebase.

# Operational Rules & Constraints
1. **Input Validation**:
   - Check if any of the following fields are empty: name, surname, email, phone, password, confirmPassword.
   - If any field is empty, trigger an `Alert.alert` indicating an error and return immediately.
   - Check if `password` matches `confirmPassword`.
   - If they do not match, trigger an `Alert.alert` indicating a mismatch and return immediately.

2. **Firebase Authentication**:
   - Use `auth().createUserWithEmailAndPassword(email, password)` to create the user.

3. **Database Storage**:
   - Upon successful authentication, create a `userDetails` object containing: name, surname, email, phone.
   - Save this object to the Firebase Realtime Database at the path `users/{result.user.uid}`.

4. **Error Handling**:
   - Catch any errors during the process and display the error message using `Alert.alert`.

# Anti-Patterns
- Do not skip the validation for empty fields or password matching.
- Do not forget to store the additional user details (name, surname, phone) in the database.

## Triggers

- write firebase registration function
- react native firebase registration with extra fields
- register user with name surname phone firebase
- react native register user with validation
- firebase auth and database registration
