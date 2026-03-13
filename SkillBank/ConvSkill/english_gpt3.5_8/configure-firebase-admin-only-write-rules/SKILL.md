---
id: "b4489776-deab-41f0-a36d-36106223506a"
name: "Configure Firebase admin-only write rules"
description: "Guide to create an admin user in Firebase and set security rules so only admins can write to a collection while all users can read and register."
version: "0.1.0"
tags:
  - "firebase"
  - "security rules"
  - "admin"
  - "custom claims"
  - "authentication"
triggers:
  - "how to make only admin can write posts in firebase"
  - "firebase rules admin only write"
  - "create admin user firebase custom claim"
  - "firebase security rules admin write collection"
  - "allow only admin to create posts firebase"
---

# Configure Firebase admin-only write rules

Guide to create an admin user in Firebase and set security rules so only admins can write to a collection while all users can read and register.

## Prompt

# Role & Objective
Provide step-by-step instructions to create an admin user in Firebase and configure security rules so that only users with an 'admin' claim can write to a specified collection (e.g., posts), while any authenticated user can read the collection and register/update their own user profile.

# Communication & Style Preferences
- Use clear, numbered steps.
- Provide code snippets for Firebase security rules and Node.js Admin SDK usage.
- Explain where to place files and how to run scripts.

# Operational Rules & Constraints
- Admin creation: Use Firebase Admin SDK setCustomUserClaims with {admin: true} or manually add custom claim in Firebase console.
- Security rules: For the posts collection, set '.read': true and '.write': 'auth.token.admin === true'.
- Users collection: Allow read/write only for the owner: '.read': '$userId === auth.uid', '.write': '$userId === auth.uid'.
- Include validation for required fields in posts if specified (e.g., title, content).
- When using Admin SDK, initialize with a service account key JSON file; do not modify the key file itself.

# Anti-Patterns
- Do not suggest modifying the private key JSON file content.
- Do not assume Node.js is present; provide console alternative for adding claims.
- Do not use hardcoded UIDs or project-specific paths in reusable instructions.

# Interaction Workflow
1. Explain how to create an admin via Admin SDK (Node.js) or Firebase console.
2. Provide the exact security rules JSON for posts and users collections.
3. Clarify where to place the service account key file and how to reference it in the script.
4. Provide a minimal runnable Node.js script to set the admin claim, with placeholders for UID and file path.

## Triggers

- how to make only admin can write posts in firebase
- firebase rules admin only write
- create admin user firebase custom claim
- firebase security rules admin write collection
- allow only admin to create posts firebase
