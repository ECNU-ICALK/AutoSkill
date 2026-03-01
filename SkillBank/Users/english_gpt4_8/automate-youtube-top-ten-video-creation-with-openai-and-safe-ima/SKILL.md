---
id: "c404420a-26e5-46f5-8133-cdfa65923942"
name: "Automate YouTube Top-Ten Video Creation with OpenAI and Safe Image Search"
description: "Integrates OpenAI API for content generation, Bing Image Search API for safe image retrieval, and Pexels API for video footage. Handles authentication via Bearer token, enforces safe search, formats ChatGPT responses into a top-ten list, and includes error handling for API failures."
version: "0.1.0"
tags:
  - "openai"
  - "api integration"
  - "video automation"
  - "content generation"
  - "image search"
triggers:
  - "generate top ten list for topic"
  - "create top ten video script"
  - "automate video creation with safe images"
  - "fetch clean images for youtube"
---

# Automate YouTube Top-Ten Video Creation with OpenAI and Safe Image Search

Integrates OpenAI API for content generation, Bing Image Search API for safe image retrieval, and Pexels API for video footage. Handles authentication via Bearer token, enforces safe search, formats ChatGPT responses into a top-ten list, and includes error handling for API failures.

## Prompt

Generate a top-ten list for a given topic in a JSON array format. Use OpenAI's /v1/completions endpoint with a specified model, temperature, and max tokens. Retrieve clean images from Bing using SafeSearch=Strict. Fetch landscape videos from Pexels. Handle API errors and None responses gracefully.

## Triggers

- generate top ten list for topic
- create top ten video script
- automate video creation with safe images
- fetch clean images for youtube
