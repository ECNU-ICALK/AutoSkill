---
id: "1d3ab876-1a2c-4569-a300-81503028531e"
name: "React Native Firebase User Registration with Password Confirmation"
description: "Generates a React Native function to handle user registration with Firebase. It validates password confirmation, creates the user account, and saves additional user profile fields (name, surname, email, phone) to a database collection."
version: "0.1.0"
tags:
  - "react native"
  - "firebase"
  - "authentication"
  - "registration"
  - "firestore"
triggers:
  - "write a firebase registration function with confirm password"
  - "react native firebase registration with extra fields"
  - "register user with name surname phone firebase"
---

# React Native Firebase User Registration with Password Confirmation

Generates a React Native function to handle user registration with Firebase. It validates password confirmation, creates the user account, and saves additional user profile fields (name, surname, email, phone) to a database collection.

## Prompt

# Role & Objective
You are a React Native developer. Write a user registration function for a React Native app using Firebase.

# Operational Rules & Constraints
1. The function must accept the following parameters: name, surname, email, phone, password, confirmPassword.
2. Implement a validation check to ensure password matches confirmPassword.
3. If passwords do not match, display an alert with the message: "Password and Confirm Password do not match!".
4. If passwords match, proceed to register the user using Firebase Authentication (createUserWithEmailAndPassword).
5. Upon successful registration, save the additional user details (name, surname, email, phone) to a 'users' collection in the database using the user's UID.
6. Handle any registration or database errors by displaying an alert with the error message.

# Output
Provide the complete JavaScript function code.

## Triggers

- write a firebase registration function with confirm password
- react native firebase registration with extra fields
- register user with name surname phone firebase
