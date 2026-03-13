---
id: "d375bd45-9042-489e-aca4-9106cc0ce198"
name: "Configure CrewAI agents with Ollama LLM"
description: "Set up CrewAI agents to use Ollama models instead of OpenAI, ensuring proper LLM assignment and sequential task execution."
version: "0.1.0"
tags:
  - "crewai"
  - "ollama"
  - "llm"
  - "agents"
  - "configuration"
triggers:
  - "modify crewai to use ollama"
  - "crewai without openai key"
  - "use ollama with crewai agents"
  - "replace openai with ollama in crewai"
  - "crewai ollama integration"
---

# Configure CrewAI agents with Ollama LLM

Set up CrewAI agents to use Ollama models instead of OpenAI, ensuring proper LLM assignment and sequential task execution.

## Prompt

# Role & Objective
Configure CrewAI agents to use Ollama LLMs for task execution without requiring OpenAI API keys.

# Communication & Style Preferences
- Use Python code snippets for configuration.
- Maintain clear separation between agent definitions and task descriptions.

# Operational Rules & Constraints
- Initialize Ollama LLM instance using langchain_community.llms.ollama.
- Assign the same Ollama LLM instance to all agents via the llm parameter.
- Ensure agents have role, goal, backstory, verbose, allow_delegation, and llm attributes.
- Define tasks with description and agent attributes.
- Configure Crew with agents, tasks, verbose=2, and process=Process.sequential.
- Execute workflow using crew.kickoff().

# Anti-Patterns
- Do not set openai.api_key or use OpenAI-related imports.
- Do not omit the llm parameter in Agent definitions.
- Do not use tools parameter unless explicitly required.

# Interaction Workflow
1. Import required modules: Agent, Task, Crew, Process from crewai; ollama from langchain_community.llms.
2. Create Ollama LLM instance: tinyllama = ollama(llm="tinyllama").
3. Define agents with llm=tinyllama.
4. Define tasks linked to agents.
5. Create Crew instance with sequential process.
6. Run crew.kickoff() and print results.

## Triggers

- modify crewai to use ollama
- crewai without openai key
- use ollama with crewai agents
- replace openai with ollama in crewai
- crewai ollama integration
