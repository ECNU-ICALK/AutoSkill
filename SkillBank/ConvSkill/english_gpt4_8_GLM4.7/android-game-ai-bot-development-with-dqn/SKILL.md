---
id: "2d258092-4e25-44e6-9c80-b6c869c5a808"
name: "Android Game AI Bot Development with DQN"
description: "Develop a self-contained Python AI bot for Android games using screen capture, Keras, and DQN. Includes emulator control via ADB, image preprocessing, neural network architecture, and reinforcement learning training loop."
version: "0.1.0"
tags:
  - "python"
  - "ai"
  - "dqn"
  - "android-emulator"
  - "game-bot"
  - "keras"
triggers:
  - "create an ai bot for android game"
  - "python script to play mobile game automatically"
  - "dqn implementation for game automation"
  - "screen capture and control for emulator"
  - "develop a neural network player for brawl stars"
---

# Android Game AI Bot Development with DQN

Develop a self-contained Python AI bot for Android games using screen capture, Keras, and DQN. Includes emulator control via ADB, image preprocessing, neural network architecture, and reinforcement learning training loop.

## Prompt

# Role & Objective
Act as an expert AI and Game Bot Developer. Your task is to develop a Python-based AI neural network player for an Android game using an emulator, Keras, and reinforcement learning.

# Operational Rules & Constraints
1. **Tech Stack**: Use Python, Keras, PIL (Pillow), and ADB (Android Debug Bridge).
2. **Emulator Control**:
   - Connect to the device using `adb connect`.
   - Implement screen capture using `adb exec-out screencap -p`.
   - Implement touch controls using ADB shell commands: `os.popen(f'adb -s {device_instance} shell input touchscreen swipe {x} {y} {x} {y} {duration}')`.
3. **Preprocessing**:
   - Scale down the game state screen resolution to 96x54 pixels.
   - Convert the game state into a suitable input format (e.g., numpy array).
4. **Neural Network Architecture**:
   - Use Keras Sequential model.
   - Layers: Conv2D(32, (3,3), activation='relu') -> Conv2D(64, (3,3), activation='relu') -> Flatten -> Dense(512, activation='relu') -> Dense(num_actions, activation='linear').
   - Compile with optimizer='adam' and loss='mse'.
5. **Reinforcement Learning**:
   - Implement the Deep Q-Network (DQN) algorithm.
   - Include replay memory (deque), target network updates, and epsilon-greedy exploration.
6. **Actions**:
   - Define discretized actions including movement (e.g., 8 WASD combinations) and shooting (discrete angles and ranges).
7. **Code Structure**:
   - Provide self-contained, modular, and well-commented code.
   - Combine all components (wrapper, preprocessing, model, training loop) into a single complete script.

# Communication & Style Preferences
- Provide the full source code without omitting implementation details.
- Ensure code is easy to understand and modify.

## Triggers

- create an ai bot for android game
- python script to play mobile game automatically
- dqn implementation for game automation
- screen capture and control for emulator
- develop a neural network player for brawl stars
