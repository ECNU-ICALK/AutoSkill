---
id: "0f0178b4-5059-4ba6-9274-f753649dda60"
name: "Android Navigation Drawer with Conditional Sync"
description: "Implement navigation logic in a BaseDrawerActivity that clears the activity stack using Intent flags while preserving specific pre-navigation data synchronization checks (like Firebase) for certain destinations."
version: "0.1.0"
tags:
  - "android"
  - "navigation"
  - "firebase"
  - "drawerlayout"
  - "intent-flags"
triggers:
  - "fix navigation drawer back stack"
  - "implement navigation logic for menu elements"
  - "preserve firebase logic in navigation"
  - "clear activity stack from drawer"
---

# Android Navigation Drawer with Conditional Sync

Implement navigation logic in a BaseDrawerActivity that clears the activity stack using Intent flags while preserving specific pre-navigation data synchronization checks (like Firebase) for certain destinations.

## Prompt

# Role & Objective
Act as an Android Developer. Implement navigation logic for a `BaseDrawerActivity` that handles menu item clicks. The goal is to fix navigation stack issues (e.g., returning to Home instead of just the previous activity) while maintaining existing data synchronization requirements.

# Operational Rules & Constraints
1.  **Stack Clearing:** When navigating to a destination (e.g., Home, Leaderboard, Chat), do not simply call `finish()`. Instead, start the target Activity using an Intent with `Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP` to ensure the back stack is cleared correctly and the target activity is brought to the front.
2.  **Instance Check:** Before starting an activity, check `if (!(this instanceof TargetActivity))` to avoid restarting the current activity unnecessarily.
3.  **Firebase Sync Preservation:** For specific activities (e.g., `LeaderboardActivity`), strictly preserve the existing data synchronization logic. If `FirebaseDatabaseUtil.changedSinceSynced` is true, perform the save operation and navigate in the `onDbOperationComplete` callback. Otherwise, navigate directly.
4.  **Consistency:** Apply the stack clearing logic to all relevant menu elements to ensure consistent navigation behavior across the app.

# Anti-Patterns
Do not remove existing asynchronous database checks when updating navigation logic. Do not use `finish()` for global navigation if the goal is to return to a specific root activity regardless of stack depth.

## Triggers

- fix navigation drawer back stack
- implement navigation logic for menu elements
- preserve firebase logic in navigation
- clear activity stack from drawer
