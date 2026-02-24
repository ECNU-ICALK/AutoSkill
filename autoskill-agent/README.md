# AutoSkill-Agent (OpenClaw External Plugin)

`autoskill-agent` is an independent evolution layer for OpenClaw-style agent workspaces.
It focuses on **agentic skill self-evolution** from successful tool-use trajectories.

## What It Does

1. `ObservationMonitor`
   - Polls OpenClaw workspace directories (for example `~/.openclaw/memory`, `runs`, `history`, `traces`).
   - Captures new `.json` / `.jsonl` trajectories.

2. `SuccessEvaluator`
   - Uses LLM-first judgment to decide whether a trajectory is usable for skill evolution.
   - Falls back to conservative heuristic scoring if LLM is unavailable.

3. `SkillSynthesizer`
   - Uses a teacher LLM (OpenAI-compatible API) to abstract reusable skills.
   - Removes instance payload and keeps reusable process constraints.

4. `SkillSetManager`
   - Receives embedding-retrieved similar skills and uses LLM to decide add / merge / discard / delete-existing.
   - Produces merged skill content when action is `merge`.

5. `SkillEmbeddingRetriever`
   - Uses embedding API to vector-retrieve the most related existing skills after extraction.
   - Keeps a local embedding cache for speed.

6. `SkillDeployer`
   - Writes one skill per folder into OpenClaw external skills directory.
   - Generates OpenClaw-compatible `SKILL.md` with frontmatter:
     - `name`
     - `description`
     - `version`
     - `tools`

## Module Split

- `plugin.py`: entrypoint only
- `engine/cli.py`: CLI args and loop control
- `engine/runtime.py`: orchestration runtime
- `engine/monitor.py`: trajectory observation/collection
- `engine/core.py`: shared data models + common helpers
- `engine/clients.py`: OpenAI-compatible LLM and embedding clients
- `engine/skill.py`: skill lifecycle (evaluate/synthesize/retrieve/manage/deploy)

## Run

```bash
python3 autoskill-agent/plugin.py \
  --workspace-dir ~/.openclaw \
  --skills-dir ~/.openclaw/skills/autoskill-agent \
  --state-dir ~/.openclaw/autoskill-agent/state \
  --trajectory-log ~/.openclaw/autoskill-agent/success_trajectories.jsonl \
  --official-llm-url https://api.openai.com \
  --official-llm-model gpt-4o-mini \
  --official-llm-api-key "$OPENCLAW_LLM_API_KEY" \
  --embedding-url https://dashscope.aliyuncs.com/compatible-mode/v1 \
  --embedding-model text-embedding-v4 \
  --embedding-api-key "$EMBEDDING_API_KEY" \
  --embedding-top-k 8 \
  --extra-llm-url https://api.deepseek.com \
  --extra-llm-model deepseek-chat \
  --extra-llm-api-key "$EXTRA_LLM_API_KEY"
```

One-shot scan mode:

```bash
python3 autoskill-agent/plugin.py --once
```

## One-Click OpenClaw Install

Install as an external plugin sidecar:

```bash
python3 autoskill-agent/integrations/openclaw/install.py \
  --workspace-dir ~/.openclaw \
  --official-llm-url https://api.openai.com \
  --official-llm-model gpt-4o-mini \
  --official-llm-api-key "$OPENCLAW_LLM_API_KEY" \
  --embedding-url https://dashscope.aliyuncs.com/compatible-mode/v1 \
  --embedding-model text-embedding-v4 \
  --embedding-api-key "$EMBEDDING_API_KEY" \
  --start
```

Generated controls:

- `~/.openclaw/plugins/autoskill-agent/start.sh`
- `~/.openclaw/plugins/autoskill-agent/stop.sh`
- `~/.openclaw/plugins/autoskill-agent/status.sh`

This keeps OpenClaw and AutoSkill-Agent decoupled while enabling one-command install and lifecycle management.

## Generic Framework Compatibility

AutoSkill-Agent can be attached to other agent frameworks without changing their core runtime.

### Option A: File Adapter (recommended)

Write normalized trajectory JSONL records into `<workspace>/runs/*.jsonl`:

```python
from integrations.generic import build_trajectory, append_trajectory

traj = build_trajectory(
    trajectory_id="run-001",
    user_instruction="Plan a 5-day family trip under budget.",
    messages=[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
    tool_calls=[{"name": "search_flights", "status": "ok", "input": {}, "output": {}}],
    environment={"framework": "langgraph"},
    success=True,
)
append_trajectory("~/.openclaw", traj)
```

### Option B: HTTP Sink

Run sink service:

```bash
python3 -m integrations.generic.trajectory_sink --workspace-dir ~/.openclaw --port 9011
```

Then any framework can POST trajectories:

```bash
curl -X POST http://127.0.0.1:9011/v1/trajectories \
  -H "Content-Type: application/json" \
  -d '{"trajectory_id":"run-1","user_instruction":"...","messages":[],"tool_calls":[],"environment":{"framework":"autogen"},"status":"completed","success":true,"completed":true}'
```

## Environment Variables

- `AUTOSKILL_AGENT_WORKSPACE_DIR`
- `AUTOSKILL_AGENT_SKILLS_DIR`
- `AUTOSKILL_AGENT_STATE_DIR`
- `AUTOSKILL_AGENT_TRAJECTORY_LOG`
- `AUTOSKILL_AGENT_LLM_URL`
- `AUTOSKILL_AGENT_LLM_MODEL`
- `AUTOSKILL_AGENT_LLM_API_KEY`
- `AUTOSKILL_AGENT_OFFICIAL_LLM_URL`
- `AUTOSKILL_AGENT_OFFICIAL_LLM_MODEL`
- `AUTOSKILL_AGENT_OFFICIAL_LLM_API_KEY`
- `AUTOSKILL_AGENT_EXTRA_LLM_URL`
- `AUTOSKILL_AGENT_EXTRA_LLM_MODEL`
- `AUTOSKILL_AGENT_EXTRA_LLM_API_KEY`
- `AUTOSKILL_AGENT_EMBEDDING_URL`
- `AUTOSKILL_AGENT_EMBEDDING_MODEL`
- `AUTOSKILL_AGENT_EMBEDDING_API_KEY`
- `AUTOSKILL_AGENT_EMBEDDING_TOP_K`
- `AUTOSKILL_AGENT_MIN_SUCCESS_SCORE`
- `AUTOSKILL_AGENT_POLL_INTERVAL_S`

## Output Layout

```text
~/.openclaw/
  autoskill-agent/
    state/
      runtime_state.json
      skill_index.json
    success_trajectories.jsonl
  skills/
    autoskill-agent/
      <skill-slug>/
        SKILL.md
        autoskill_agent.meta.json
```
