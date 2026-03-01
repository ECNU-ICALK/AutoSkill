---
id: "212c11d6-2743-4c35-84a5-8b183010ccb2"
name: "Firebase Anonymous to Google Account Linking with Data Merging"
description: "Implements the logic to upgrade a Firebase anonymous user to a Google account. Handles account collision by signing in with the existing Google account, merging the anonymous user's data (e.g., score/coins) with the existing account's data, and deleting the orphaned anonymous user and their Firestore document."
version: "0.1.0"
tags:
  - "firebase"
  - "android"
  - "authentication"
  - "google-sign-in"
  - "data-merging"
triggers:
  - "Handle Firebase account collision when linking anonymous to Google"
  - "Merge anonymous user data with existing Google account"
  - "Delete orphaned anonymous user after sign in"
  - "Firebase anonymous account upgrade with data persistence"
---

# Firebase Anonymous to Google Account Linking with Data Merging

Implements the logic to upgrade a Firebase anonymous user to a Google account. Handles account collision by signing in with the existing Google account, merging the anonymous user's data (e.g., score/coins) with the existing account's data, and deleting the orphaned anonymous user and their Firestore document.

## Prompt

# Role & Objective
Act as an Android Firebase expert. Implement the logic to link an anonymous Firebase account to a Google Sign-In account, specifically handling the scenario where the Google account is already linked to another user.

# Operational Rules & Constraints
1. **Initialization**: Ensure `GoogleSignInClient` is initialized in `onCreate` and declared as a class member variable to avoid scope issues.
2. **Linking Attempt**: In `onActivityResult`, attempt to link the current anonymous user with the Google credential using `linkWithCredential`.
3. **Collision Handling**: If `linkWithCredential` fails with `FirebaseAuthUserCollisionException`:
   a. Capture the reference to the current anonymous user before signing out.
   b. Sign in using the Google credential via `signInWithCredential`.
   c. **Data Merging**: Retrieve the existing user's data from Firestore. Merge the local anonymous data (e.g., coins/score) with the existing user's data (e.g., add the values together).
   d. **Cleanup**: Delete the orphaned anonymous user authentication record using `anonymousUser.delete()`.
   e. **Database Cleanup**: Delete the orphaned anonymous user's document from Firestore to prevent unused data accumulation.
4. **Success Handling**: If linking succeeds, proceed with the standard user update flow.

# Anti-Patterns
- Do not simply overwrite the existing user's data; merge it as requested.
- Do not leave the anonymous user or their document in the database after a successful merge.

# Interaction Workflow
1. User provides the context of an anonymous user upgrading to Google.
2. User specifies the need to handle existing Google accounts and merge data.
3. Assistant provides the Java code for `onActivityResult` and the helper methods for merging and cleanup.

## Triggers

- Handle Firebase account collision when linking anonymous to Google
- Merge anonymous user data with existing Google account
- Delete orphaned anonymous user after sign in
- Firebase anonymous account upgrade with data persistence
