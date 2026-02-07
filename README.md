# AutoSkill: Experience-Driven Lifelong Learning via Skill Self-Evolution

English | [中文](README.zh-CN.md)

AutoSkill is a practical implementation of **Experience-driven Lifelong Learning (ELL)**.
It learns from real interaction experience (dialogue + behavior/events), automatically creates reusable Skills,
and continuously evolves existing Skills through merge + version updates.

Instead of storing raw memory fragments, AutoSkill stores **portable Agent Skills** (`SKILL.md`)
that can be retrieved and reused in future tasks and even migrated to other agent systems.

## 1. Start Here: Web UI

```bash
python3 -m pip install -e .
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.web_ui \
  --host 127.0.0.1 \
  --port 8000 \
  --llm-provider dashscope \
  --embeddings-provider dashscope \
  --store-dir Skills \
  --user-id u1 \
  --skill-scope all \
  --rewrite-mode always \
  --extract-mode auto \
  --extract-turn-limit 1 \
  --min-score 0.4 \
  --top-k 1
```

Open `http://127.0.0.1:8000`.

## 1.1 OpenAI-Compatible Proxy (Standard API)

AutoSkill can also be deployed as a reverse proxy that exposes OpenAI-compatible endpoints while transparently applying:
- skill retrieval/injection for each chat request
- asynchronous skill extraction/maintenance after responses

```bash
python3 -m pip install -e .
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.openai_proxy \
  --host 127.0.0.1 \
  --port 9000 \
  --llm-provider dashscope \
  --embeddings-provider dashscope \
  --store-dir Skills \
  --user-id u1 \
  --skill-scope all \
  --rewrite-mode always \
  --min-score 0.4 \
  --top-k 1
```

Endpoints:
- `POST /v1/chat/completions` (supports `stream=true`)
- `POST /v1/embeddings`
- `GET /v1/models`
- `GET /health`

Per-request user isolation:
- request body field `user` (recommended)
- or header `X-AutoSkill-User`

## 1.2 Skill Lifecycle Example (4 Aspects)

### A) Auto Decision: No Extraction for Generic One-shot Tasks

If the user only asks to "write a report" and gives no stable preference/correction, AutoSkill does **not** create a new skill
(it outputs an empty extraction result) to avoid noisy, generic skills.

### B) Feedback-triggered Extraction + Management (v0.1.0)

![Skill Extraction](imgs/skill_extraction.png)

When the user adds durable constraints (for example: "do not hallucinate"), AutoSkill extracts or merges a skill into version `v0.1.0`.
Skill management is backend-first (automatic add/merge), with optional human edit/save/delete of `SKILL.md`.

### C) Skill Update (v0.1.1)

When user feedback adds new constraints or changes priorities in later turns, AutoSkill updates the existing skill (instead of creating duplicates)
and evolves the version from `v0.1.0` to `v0.1.1`.

![Skill Update](imgs/skill_update.png)

### D) Skill Usage

For the next similar task (for example, writing a **government report about a self-evolving agent**), the updated skill is retrieved and used
to generate outputs aligned with user expectations.

![Skill Usage](imgs/skill_utilize.png)

## 2. What Makes AutoSkill Different

- **Experience-native learning**: learns directly from user/assistant interactions and behavior traces.
- **Continuous skill evolution**: not only adds new skills, but also merges/improves similar existing skills with version bumps.
- **Feedback-gated extraction**: generic one-shot tasks are filtered out; stable user feedback (e.g., "no hallucination") triggers extraction/update.
- **Portable skill artifact**: stores skills in Agent Skill format (`SKILL.md`), so existing skills can be imported and extracted skills can be migrated.
- **Personal + shared knowledge planes**: supports both user-private skills (`Users/<user_id>`) and shared libraries (`Common/`) in one retrieval flow.
- **Standards-compatible serving**: OpenAI-compatible proxy API lets existing clients use AutoSkill with no business-logic changes.

## 3. System Workflow

![AutoSkill Framework](imgs/Framework.png)

### 3.1 Ingest and Evolve

```text
Experience (messages/events)
  -> Skill Extraction (candidate)
  -> Skill Maintenance (add / merge / discard)
  -> Skill Store (Agent Skill artifact + vector index)
```

- Extractor emits at most one high-quality candidate per attempt.
- Maintainer checks similarity against existing skills, then decides add/merge/discard.
- Merge updates preserve and improve capabilities, then bump patch version.

### 3.2 Retrieve and Respond

```text
User Query (+ recent history)
  -> Query Rewrite (optional)
  -> Embedding + Vector Search
  -> Skill Selection for Context
  -> LLM Response
```

- Retrieval runs every turn.
- Similarity threshold and `top_k` control precision/recall.
- Retrieved skills are filtered again before context injection.

### 3.3 Interactive Extraction Policy

- `extract_mode=auto`: attempt extraction every `extract_turn_limit` turns.
- `extract_mode=always`: attempt every turn.
- `extract_mode=never`: disable auto extraction.
- `extract_now [hint]`: force immediate background extraction for current context.
- Generic requests without user correction (for example, one-time report writing) should return no skill extraction.
- User feedback that encodes durable preferences/constraints (for example, "do not hallucinate") should trigger extraction or update.
- If a similar user skill already exists, prefer merge/update over creating a duplicate skill.

### 3.4 Proxy Serving Flow

```text
Client (OpenAI-compatible request)
  -> AutoSkill Proxy (/v1/chat/completions)
  -> Query rewrite + skill retrieval + context injection
  -> Upstream model generation
  -> Return response to client
  -> Async skill extraction/maintenance (background)
```

- Response latency focuses on retrieval + generation.
- Skill evolution runs asynchronously to avoid blocking the client.

## 4. Key Concepts

- **Experience**: dialogue messages or behavior/event records used as learning signal.
- **Skill**: reusable capability artifact with metadata + executable instructions.
- **Skill Candidate**: temporary extraction output before maintenance decisions.
- **Maintenance**: logic that decides add/merge/discard and handles versioning.
- **Skill Store**: persistence layer for skill artifacts and vector mappings.
- **Retrieval Context**: selected skills rendered into prompt context for answering.

## 5. Storage Layout (Local Store)

When using `store={"provider": "local", "path": "Skills"}`:

```text
Skills/
  Users/
    <user_id>/
      <skill-slug>/
        SKILL.md
        scripts/          (optional)
        references/       (optional)
        assets/           (optional)
  Common/
    <skill-slug>/SKILL.md
    <library>/<skill-slug>/SKILL.md
  vectors/
    <embedding-signature>.meta.json
    <embedding-signature>.ids.txt
    <embedding-signature>.vecs.f32
```

Notes:

- `Users/<user_id>`: user-specific skills.
- `Common/`: shared library skills (read-only in normal interactive usage).
- `vectors/`: persistent vector cache keyed by embedding signature, so switching embedding models will build/use separate indexes.

## 6. Repository Structure (Readable Map)

### 6.1 Top Level

- `autoskill/`: SDK core.
- `examples/`: runnable demos and entry scripts.
- `autoskill/proxy/`: OpenAI-compatible reverse proxy runtime.
- `web/`: static frontend assets for local Web UI.
- `Skills/`: default local storage root.
- `imgs/`: README demo images.

### 6.2 Core SDK Modules

- `autoskill/client.py`: public SDK entrypoint (`ingest`, `search`, `render_context`, import/export).
- `autoskill/config.py`: global config model.
- `autoskill/models.py`: core data models (`Skill`, `SkillHit`, etc.).
- `autoskill/render.py`: convert selected skills into injectable context.

### 6.3 Skill Management Layer

- `autoskill/skill_management/extraction.py`: extraction logic and prompts.
- `autoskill/skill_management/maintenance.py`: merge/version/add-discard decisions.
- `autoskill/skill_management/formats/agent_skill.py`: `SKILL.md` render/parse.
- `autoskill/skill_management/stores/local.py`: directory-based storage + vector mapping.
- `autoskill/skill_management/vectors/flat.py`: on-disk vector index backend.
- `autoskill/skill_management/importer.py`: import external Agent Skills.

### 6.4 Interactive Layer

- `autoskill/interactive/app.py`: terminal interactive app orchestration.
- `autoskill/interactive/session.py`: headless session engine for Web/API usage.
- `autoskill/interactive/rewriting.py`: query rewriting for better retrieval.
- `autoskill/interactive/selection.py`: optional LLM skill selection before injection.

### 6.5 Example Entrypoints

- `examples/web_ui.py`: local Web UI server.
- `examples/interactive_chat.py`: CLI interactive chat.
- `examples/import_agent_skills.py`: bulk import existing skills.
- `examples/normalize_skill_ids.py`: normalize missing IDs in `SKILL.md`.
- `examples/local_persistent_store.py`: offline local persistence demo.
- `examples/openai_proxy.py`: OpenAI-compatible proxy entrypoint.

## 7. Quick SDK Usage

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={"provider": "mock"},
        embeddings={"provider": "hashing", "dims": 256},
        store={"provider": "local", "path": "Skills"},
    )
)

sdk.ingest(
    user_id="u1",
    messages=[
        {"role": "user", "content": "Before each release: run regression -> canary -> monitor -> full rollout."},
        {"role": "assistant", "content": "Understood."},
    ],
)

hits = sdk.search("How should I do a safe release?", user_id="u1", limit=3)
for h in hits:
    print(h.skill.name, h.score)
```

## 8. Provider Setup

### 8.1 DashScope (Example)

```bash
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.interactive_chat --llm-provider dashscope
```

### 8.2 GLM (BigModel)

```bash
export ZHIPUAI_API_KEY="YOUR_ID.YOUR_SECRET"
python3 -m examples.interactive_chat --llm-provider glm
```

### 8.3 OpenAI / Anthropic

```bash
export OPENAI_API_KEY="YOUR_OPENAI_KEY"
python3 -m examples.interactive_chat --llm-provider openai

export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_KEY"
python3 -m examples.interactive_chat --llm-provider anthropic
```

## 9. Common Workflows

### 9.1 Interactive Chat (retrieve every turn)

```bash
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.interactive_chat --llm-provider dashscope
```

Useful commands:

- `/extract_now [hint]`
- `/extract_every <n>`
- `/extract auto|always|never`
- `/scope user|common|all`
- `/search <query>`
- `/skills`
- `/export <skill_id>`

### 9.2 Web UI

```bash
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.web_ui --llm-provider dashscope
```

### 9.3 Import Existing Agent Skills

```bash
python3 -m examples.import_agent_skills --root-dir /path/to/skills --scope common --store-dir Skills
```

### 9.4 Normalize Missing Skill IDs

```bash
python3 -m examples.normalize_skill_ids --store-dir Skills
```

### 9.5 OpenAI-Compatible Proxy API

```bash
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.openai_proxy --llm-provider dashscope --embeddings-provider dashscope
```

Discoverability:

```bash
curl http://127.0.0.1:9000/v1/autoskill/capabilities
curl http://127.0.0.1:9000/v1/autoskill/openapi.json
```

OpenAI-compatible:

- `POST /v1/chat/completions`
- `POST /v1/embeddings`
- `GET /v1/models`

Skill APIs:

- `GET /v1/autoskill/skills`
- `GET /v1/autoskill/skills/{skill_id}`
- `GET /v1/autoskill/skills/{skill_id}/md`
- `PUT /v1/autoskill/skills/{skill_id}/md`
- `DELETE /v1/autoskill/skills/{skill_id}`
- `POST /v1/autoskill/skills/{skill_id}/rollback`
- `GET /v1/autoskill/skills/{skill_id}/versions`
- `GET /v1/autoskill/skills/{skill_id}/export`
- `POST /v1/autoskill/skills/search`
- `POST /v1/autoskill/skills/import`

Retrieval and extraction:

- `POST /v1/autoskill/retrieval/preview`
- `POST /v1/autoskill/extractions`
- `POST /v1/autoskill/extractions/simulate`
- `GET /v1/autoskill/extractions/latest`
- `GET /v1/autoskill/extractions`
- `GET /v1/autoskill/extractions/{job_id}`
- `GET /v1/autoskill/extractions/{job_id}/events` (SSE)

Vector admin:

- `GET /v1/autoskill/vectors/status`
- `POST /v1/autoskill/vectors/rebuild`

Chat completion example:

```bash
curl http://127.0.0.1:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "YOUR_MODEL_NAME",
    "user": "u1",
    "messages": [
      {"role": "user", "content": "Write a concise release checklist."}
    ]
  }'
```

Retrieval preview example:

```bash
curl http://127.0.0.1:9000/v1/autoskill/retrieval/preview \
  -H "Content-Type: application/json" \
  -d '{
    "user": "u1",
    "query": "Write a concise government report with no hallucinations."
  }'
```

Extraction event stream example:

```bash
curl -N http://127.0.0.1:9000/v1/autoskill/extractions/<job_id>/events \
  -H "Accept: text/event-stream"
```

Vector rebuild example:

```bash
curl http://127.0.0.1:9000/v1/autoskill/vectors/rebuild \
  -H "Content-Type: application/json" \
  -d '{
    "user": "u1",
    "scope": "all",
    "force": true,
    "blocking": true
  }'
```

## 10. Why This Matters

AutoSkill turns short-term interaction into long-term capability.

- It reduces manual Skill authoring cost.
- It keeps capabilities aligned with real user feedback over time.
- It enables a transferable skill ecosystem across different agent runtimes.

In short, this framework is a concrete path from prompt engineering to **experience-driven lifelong agent learning**.

## 11. Citation

If you use AutoSkill in academic work, technical reports, or demos, please cite:

```bibtex
@software{autoskill_2026,
  author = {ECNU-ICALK},
  title = {AutoSkill: Experience-Driven Lifelong Learning via Skill Self-Evolution},
  year = {2026},
  url = {https://github.com/ECNU-ICALK/AutoSkill},
  note = {GitHub repository}
}
```
