# AutoSkill OpenClaw Plugin

`AutoSkill-OpenClaw-Plugin` is a local sidecar service that plugs AutoSkill into OpenClaw for:

- skill retrieval (`query rewrite + retrieval`)
- asynchronous skill evolution (`extract + add/merge/discard`)

## 1. Repository and Local Paths

- GitHub source:
- [https://github.com/ECNU-ICALK/AutoSkill/tree/main/OpenClaw-Plugin](https://github.com/ECNU-ICALK/AutoSkill/tree/main/OpenClaw-Plugin)

- Runtime install path (created by installer):
- `~/.openclaw/plugins/autoskill-openclaw-plugin`

- OpenClaw native adapter path (auto-installed):
- `~/.openclaw/extensions/autoskill-openclaw-adapter`

- OpenClaw config (auto-updated by installer):
- `~/.openclaw/openclaw.json`

- Skill storage (default):
- `~/.openclaw/autoskill/SkillBank`

## 2. Features

- Hook-style retrieval API (MemOS-like):
- `POST /v1/autoskill/openclaw/hooks/before_agent_start`

- Hook-style post-run evolution API (MemOS-like):
- `POST /v1/autoskill/openclaw/hooks/agent_end`

- Backward-compatible per-turn API:
- `POST /v1/autoskill/openclaw/turn`

- Background extraction/evolution APIs:
- `POST /v1/autoskill/extractions`
- `GET /v1/autoskill/extractions/latest`
- `GET /v1/autoskill/extractions`
- `GET /v1/autoskill/extractions/{job_id}`
- `GET /v1/autoskill/extractions/{job_id}/events`

- Conversation import for offline evolution:
- `POST /v1/autoskill/conversations/import`

- Skill management APIs:
- `POST /v1/autoskill/skills/search`
- `GET /v1/autoskill/skills`
- `GET /v1/autoskill/skills/{skill_id}`
- `PUT /v1/autoskill/skills/{skill_id}/md`
- `DELETE /v1/autoskill/skills/{skill_id}`
- `POST /v1/autoskill/skills/{skill_id}/rollback`

## 3. Runtime Flow

Recommended hook lifecycle:

1. OpenClaw calls `before_agent_start`.
2. Service rewrites query (optional), retrieves skills, and returns `context_message`.
3. OpenClaw injects `context_message` into model input and runs its normal agent/model loop.
4. OpenClaw calls `agent_end` with final messages and optional success signal.
5. Service schedules extraction in background and updates `SkillBank`.

Note:
- `agent_end` supports success gating (`success`/`task_success`/`objective_met`).
- Existing `/v1/autoskill/openclaw/turn` remains available for single-call integration.
- The installer writes adapter load path + plugin entry into `~/.openclaw/openclaw.json`, so no manual hook wiring is required.
- If `openclaw.json` is invalid JSON, installer will stop instead of overwriting it.
- The adapter uses OpenClaw native hook registration (`registerHook`) with fallback to `on` for compatibility.

## 4. Prerequisites

- Python 3.10+
- AutoSkill repository available locally
- Valid LLM + embedding credentials in plugin `.env` (or environment)

## 5. Installation

### Option A: Install from GitHub Source

```bash
git clone https://github.com/ECNU-ICALK/AutoSkill.git
cd AutoSkill
python3 -m pip install -e .
python3 OpenClaw-Plugin/install.py \
  --workspace-dir ~/.openclaw \
  --install-dir ~/.openclaw/plugins/autoskill-openclaw-plugin \
  --adapter-dir ~/.openclaw/extensions/autoskill-openclaw-adapter \
  --repo-dir "$(pwd)" \
  --llm-provider internlm \
  --llm-model intern-s1-pro \
  --embeddings-provider qwen \
  --embeddings-model text-embedding-v4
```

### Option B: Install from Existing Local Path

```bash
cd /path/to/AutoSkill
python3 -m pip install -e .
python3 OpenClaw-Plugin/install.py \
  --workspace-dir ~/.openclaw \
  --install-dir ~/.openclaw/plugins/autoskill-openclaw-plugin \
  --adapter-dir ~/.openclaw/extensions/autoskill-openclaw-adapter \
  --repo-dir "$(pwd)" \
  --llm-provider internlm \
  --llm-model intern-s1-pro \
  --embeddings-provider qwen \
  --embeddings-model text-embedding-v4
```

Generated files:

- `~/.openclaw/plugins/autoskill-openclaw-plugin/.env`
- `~/.openclaw/plugins/autoskill-openclaw-plugin/run.sh`
- `~/.openclaw/plugins/autoskill-openclaw-plugin/start.sh`
- `~/.openclaw/plugins/autoskill-openclaw-plugin/stop.sh`
- `~/.openclaw/plugins/autoskill-openclaw-plugin/status.sh`
- `~/.openclaw/extensions/autoskill-openclaw-adapter/index.js`
- `~/.openclaw/extensions/autoskill-openclaw-adapter/openclaw.plugin.json`
- `~/.openclaw/extensions/autoskill-openclaw-adapter/package.json`
- `~/.openclaw/openclaw.json` (updated: `plugins.load.paths` + `plugins.entries.autoskill-openclaw-adapter`)

## 6. Startup Workflows

### Workflow A: Install Once, Then Start Sidecar

1. Edit plugin env:

```bash
vim ~/.openclaw/plugins/autoskill-openclaw-plugin/.env
```

Required fields usually include:

- `INTERNLM_API_KEY` (or your selected LLM provider key)
- `DASHSCOPE_API_KEY` (if using qwen embedding)
- `AUTOSKILL_PROXY_API_KEY` (optional)

2. Start service:

```bash
~/.openclaw/plugins/autoskill-openclaw-plugin/start.sh
~/.openclaw/plugins/autoskill-openclaw-plugin/status.sh
```

3. Verify service:

```bash
curl http://127.0.0.1:9100/health
curl http://127.0.0.1:9100/v1/autoskill/capabilities
```

4. Restart OpenClaw runtime so it reloads plugin config from `~/.openclaw/openclaw.json`.

5. (Optional) confirm adapter entry:

```bash
cat ~/.openclaw/openclaw.json
```

Expected fields:
- `plugins.load.paths` includes `~/.openclaw/extensions/autoskill-openclaw-adapter`
- `plugins.entries.autoskill-openclaw-adapter.enabled = true`
- `plugins.entries.autoskill-openclaw-adapter.config.baseUrl = http://127.0.0.1:9100/v1`
- If sidecar auth is enabled, set `plugins.entries.autoskill-openclaw-adapter.config.apiKey`
  or provide `AUTOSKILL_PROXY_API_KEY` in OpenClaw runtime environment.

### Workflow B: Install and Start in One Command

```bash
python3 OpenClaw-Plugin/install.py \
  --workspace-dir ~/.openclaw \
  --install-dir ~/.openclaw/plugins/autoskill-openclaw-plugin \
  --adapter-dir ~/.openclaw/extensions/autoskill-openclaw-adapter \
  --repo-dir "$(pwd)" \
  --llm-provider internlm \
  --llm-model intern-s1-pro \
  --embeddings-provider qwen \
  --embeddings-model text-embedding-v4 \
  --start
```

Then verify:

```bash
curl http://127.0.0.1:9100/health
```

Important:
- Restart OpenClaw runtime once after installation/start, otherwise the adapter hook config may not be loaded yet.

If you do not want auto config patch:

```bash
python3 OpenClaw-Plugin/install.py --skip-openclaw-config-update
```

## 7. OpenClaw Call Examples

### 7.1 Hook: before_agent_start (retrieve + context injection payload)

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/openclaw/hooks/before_agent_start \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role":"user","content":"Write a government report. No table. Avoid hallucinations."}
    ]
  }'
```

Response includes:

- `hits` / `selected_for_context_ids`
- `context`
- `context_message` (directly append as system message in OpenClaw runtime)

### 7.2 Hook: agent_end (async extraction/evolution)

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/openclaw/hooks/agent_end \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role":"user","content":"Write a government report. No table. Avoid hallucinations."},
      {"role":"assistant","content":"Draft report ..."},
      {"role":"user","content":"Make it sharper and more specific."},
      {"role":"assistant","content":"Updated draft ..."}
    ],
    "success": true,
    "user_feedback": "Good, keep this writing policy for next time."
  }'
```

### 7.3 Compatibility: single-call turn API

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/openclaw/turn \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role":"assistant","content":"How should I write it?"},
      {"role":"user","content":"Write a government report. No table. Avoid hallucinations."}
    ],
    "schedule_extraction": true
  }'
```

### 7.4 Offline Conversation Import

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/conversations/import \
  -H "Content-Type: application/json" \
  -d '{
    "conversations": [
      {
        "messages": [
          {"role":"user","content":"Write a policy memo."},
          {"role":"assistant","content":"Draft ..."},
          {"role":"user","content":"More specific and avoid hallucinations."}
        ]
      }
    ]
  }'
```

### 7.5 Extraction Event Stream

```bash
curl -N http://127.0.0.1:9100/v1/autoskill/extractions/<job_id>/events \
  -H "Accept: text/event-stream"
```

## 8. User ID Routing

User id resolution order:

1. request body `user`
2. header `X-AutoSkill-User`
3. `Authorization: Bearer <JWT>` payload field `id`
4. fallback `AUTOSKILL_USER_ID`

## 9. Lifecycle Commands

```bash
~/.openclaw/plugins/autoskill-openclaw-plugin/start.sh
~/.openclaw/plugins/autoskill-openclaw-plugin/status.sh
~/.openclaw/plugins/autoskill-openclaw-plugin/stop.sh
```

Logs:

- `~/.openclaw/plugins/autoskill-openclaw-plugin/autoskill-openclaw-plugin.log`

## 10. Key Environment Variables

- `AUTOSKILL_PROXY_HOST` (default `127.0.0.1`)
- `AUTOSKILL_PROXY_PORT` (default `9100`)
- `AUTOSKILL_STORE_DIR` (default `~/.openclaw/autoskill/SkillBank`)
- `AUTOSKILL_LLM_PROVIDER` / `AUTOSKILL_LLM_MODEL`
- `AUTOSKILL_EMBEDDINGS_PROVIDER` / `AUTOSKILL_EMBEDDINGS_MODEL`
- `AUTOSKILL_REWRITE_MODE` (`never|auto|always`)
- `AUTOSKILL_SKILL_SCOPE` (`user|library|all`)
- `AUTOSKILL_MIN_SCORE` / `AUTOSKILL_TOP_K`
- `AUTOSKILL_INGEST_WINDOW`
- `AUTOSKILL_EXTRACT_ENABLED`
- `AUTOSKILL_PROXY_API_KEY` (optional)
