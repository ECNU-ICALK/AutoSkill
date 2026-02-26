# AutoSkill OpenClaw Plugin

`AutoSkill-OpenClaw-Plugin` is a local sidecar service that plugs AutoSkill into OpenClaw for:

- skill retrieval (`query rewrite + retrieval`)
- asynchronous skill evolution (`extract + add/merge/discard`)

## 1. Repository and Local Paths

- GitHub source:
- [https://github.com/ECNU-ICALK/AutoSkill/tree/main/OpenClaw-Plugin](https://github.com/ECNU-ICALK/AutoSkill/tree/main/OpenClaw-Plugin)

- Runtime install path (created by installer):
- `~/.openclaw/plugins/autoskill-openclaw-plugin`

- Skill storage (default):
- `~/.openclaw/autoskill/SkillBank`

## 2. Features

- Per-turn retrieval API for OpenClaw:
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

For each OpenClaw turn:

1. OpenClaw sends recent messages to `/v1/autoskill/openclaw/turn`.
2. Service rewrites query (optional) and retrieves related skills.
3. Service returns retrieval result/context immediately.
4. Service schedules extraction in background.
5. Background worker updates `SkillBank`.

Note:
- Extraction scheduling requires latest turn `user` and at least one prior `assistant` turn in the window.

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

## 6. Startup Workflows

### Workflow A: Start Service First, Then Connect OpenClaw

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

4. Connect OpenClaw to:

- `base_url`: `http://127.0.0.1:9100/v1`
- `api_key`: `AUTOSKILL_PROXY_API_KEY` value (or empty)
- main endpoint: `POST /v1/autoskill/openclaw/turn`

### Workflow B: Install and Start in One Command

```bash
python3 OpenClaw-Plugin/install.py \
  --workspace-dir ~/.openclaw \
  --install-dir ~/.openclaw/plugins/autoskill-openclaw-plugin \
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

## 7. OpenClaw Call Examples

### 7.1 Turn Retrieval + Background Extraction Scheduling

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

### 7.2 Offline Conversation Import

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

### 7.3 Extraction Event Stream

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

