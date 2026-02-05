# AutoSkill SDK

English | [中文](README.zh-CN.md)

AutoSkill is a self-evolving “Skill Layer” SDK that turns conversations and behavior/event logs into reusable,
executable **Skills**, continuously maintains them (dedupe/merge/versioning), and retrieves/injects the right
Skills to improve downstream task performance over time.

Goal: similar to a "memory plugin" workflow, but the stored unit is an executable, reusable Skill rather than
raw memory.

## Install (local dev)

```bash
python3 -m pip install -e .
```

## Quickstart

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={"provider": "mock"},
        embeddings={"provider": "hashing", "dims": 256},
        store={"provider": "inmemory"},  # or {"provider": "local", "path": "Skills"}
    )
)

sdk.ingest(
    messages=[
        {"role": "user", "content": "Before each release: run regression tests -> canary rollout -> monitor -> full rollout."},
        {"role": "assistant", "content": "Got it."},
    ],
    user_id="u1",
)

hits = sdk.search("How should I do a release?", user_id="u1", limit=5)
for h in hits:
    print(h.skill.name, h.score)
```

## Provider Config Examples

OpenAI:

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={"provider": "openai", "model": "gpt-4o-mini", "api_key": "YOUR_KEY"},
        embeddings={
            "provider": "openai",
            "model": "text-embedding-3-small",
            "api_key": "YOUR_KEY",
        },
        store={"provider": "inmemory"},
        maintenance_strategy="llm",
    )
)
```

DashScope Qwen (OpenAI-compatible mode):

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={
            "provider": "dashscope",
            "model": "qwen-plus",
            "api_key": "YOUR_DASHSCOPE_API_KEY",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode",
        },
        embeddings={
            "provider": "dashscope",
            "model": "text-embedding-v4",
            "api_key": "YOUR_DASHSCOPE_API_KEY",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode",
            "extra_body": {"dimensions": 1024, "encoding_format": "float"},
        },
        store={"provider": "inmemory"},
        maintenance_strategy="llm",
    )
)
```

Anthropic:

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={"provider": "anthropic", "model": "claude-3-5-sonnet-latest", "api_key": "YOUR_KEY"},
        embeddings={"provider": "hashing", "dims": 256},
        store={"provider": "inmemory"},
        maintenance_strategy="llm",
    )
)
```

BigModel GLM (GLM-4.7 + embedding-3):

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={
            "provider": "glm",
            "model": "glm-4.7",
            "api_key": "YOUR_ID.YOUR_SECRET",
            "auth_mode": "auto",  # default: "auto"; can force "jwt" or "api_key"
        },
        embeddings={
            "provider": "glm",
            "model": "embedding-3",
            "api_key": "YOUR_ID.YOUR_SECRET",
            "auth_mode": "auto",  # default: "auto"; can force "jwt" or "api_key"
        },
        store={"provider": "inmemory"},
        maintenance_strategy="llm",
    )
)
```

## SDK Capabilities

- `ingest(...)`: extract/update Skills from `messages` (chat) or `events` (logs)
- `search(query, ...)`: retrieve Skills relevant to the current task
- `get(skill_id)` / `list(user_id)` / `delete(skill_id)`
- `render_context(query, ...)`: render retrieved Skills into an injectible context block

## Skill Format (Agent Skill / anthropics/skills style)

Internally, a Skill is represented as a structured object and can be exported as an **Agent Skill directory
artifact** (a directory containing `SKILL.md`) for saving and maintenance (inspired by `anthropics/skills`).

Core fields:

- `name`: short, searchable title
- `description`: what the skill is for
- `instructions` (aka `prompt`): reusable, directly executable instructions for an LLM/Agent
- `triggers`: when to apply the skill
- `examples`: representative examples (optional)
- `tags`: topical tags
- `version`: semantic version (default `0.1.0`, bump patch on merges)

Agent Skill artifact:

- `Skill.files["SKILL.md"]`: generated `SKILL.md` (YAML frontmatter + Markdown body)
- `AutoSkill.export_skill_md(skill_id)`: export `SKILL.md` text
- `AutoSkill.write_skill_dir(skill_id, root_dir=...)`: write a skill directory containing `SKILL.md` (scripts/resources can be added)
- `AutoSkill.write_skill_dirs(user_id=..., root_dir=...)`: write all skills for a user into directories

You can further align this schema to the exact conventions used in `anthropics/skills`; this SDK keeps the
storage/interface flexible for extensions.

## LLM / Embeddings / Store

AutoSkill uses a pluggable architecture:

- LLM: `mock` (offline), `openai`, `dashscope` (Qwen), `anthropic`, `glm` (BigModel GLM-4.7)
- Embeddings: `hashing` (offline), `openai`, `dashscope` (Qwen), `glm` (BigModel embedding-3)
- Store: `inmemory` (offline), `local` (directory-based persistence: `Users/<user_id>/...` + optional shared `Common/...`; caches vectors in a persistent on-disk index for fast retrieval)

## Architecture

AutoSkill is organized into a few composable layers (similar to Mem0's "client + provider + store" split),
with an additional Skill Management layer for extraction + maintenance.

### Core Data Flow

**Ingest (grow/maintain skills):**

1) `AutoSkill.ingest(...)` receives `messages` (chat) or `events` (behavior logs)
2) `SkillExtractor.extract(...)` produces up to 1 `SkillCandidate` (LLM-based or heuristic)
3) `SkillMaintainer.apply(...)` decides add/merge/discard by searching similar skills, then upserts the result
4) `SkillStore.upsert(...)` persists a skill as an Agent Skill artifact (`SKILL.md` + optional resources)

**Retrieve (use skills):**

1) (optional) rewrite a user query into a better retrieval query (focus on capability/need, not pasted content)
2) embed the query via the configured embeddings provider
3) `SkillStore.search(...)` runs vector search over stored skill embeddings and returns `SkillHit`s
4) render selected skills into an injectable context block (`render_skills_context(...)`)

### Persistence Layout (Local Store)

When `store={"provider":"local","path":"Skills"}`, the recommended on-disk layout is:

```text
Skills/
  Users/
    <user_id>/
      <skill-slug>/
        SKILL.md
        scripts/…            (optional)
        references/…         (optional)
        assets/…             (optional)
  Common/
    <skill-slug>/SKILL.md
    <library-name>/<skill-slug>/SKILL.md
  vectors/
    <index>.meta.json
    <index>.ids.txt
    <index>.vecs.f32
```

Notes:
- `Common/` is the shared library. `Users/<user_id>/` is user-private skills.
- Additional read-only libraries can be added via `--library-dir` (see examples).
- Vector caches are stored per embedding signature (provider + model + optional dimensions) to avoid mixing
  vectors when you switch embedding models.

### Interactive Flow (Retrieve + Extract)

In `autoskill.interactive`, each user turn runs retrieval before generating the assistant response.
Extraction is attempted on a fixed schedule; in `auto` mode it runs once every N turns (`extract_turn_limit`, default `1`).
The extractor itself decides whether to emit a Skill (by returning `{"skills": []}` when there is not enough
reusable signal), and ingestion runs on the next user message (so it can include that message as light feedback context).

## Repository Structure (Code Map)

This section is a quick “what lives where” map. Paths are relative to the repo root.

### Top-Level

- `README.md`: overview, provider configs, usage examples, architecture map
- `pyproject.toml`: packaging + dependencies
- `Skills/`: default local store root (created/used at runtime)
- `web/`: static assets for the local Web UI (`examples/web_ui.py`)
- `autoskill/`: SDK package (core implementation)
- `examples/`: runnable scripts showing end-to-end flows

### `autoskill/` (SDK)

- `autoskill/__init__.py`: public exports (`AutoSkill`, `AutoSkillConfig`, models)
- `autoskill/client.py`: SDK entrypoint (ingest/search/render/export/import)
- `autoskill/config.py`: `AutoSkillConfig` (serializable config + defaults)
- `autoskill/models.py`: core models (`Skill`, `SkillHit`, `SkillExample`, status enums)
- `autoskill/render.py`: render selected skills into an injectable context block
- `autoskill/py.typed`: marker for type checkers (package ships type hints)

#### `autoskill/llm/` (Chat LLM Providers)

- `autoskill/llm/__init__.py`: provider-layer exports (`LLM`, `build_llm`)
- `autoskill/llm/base.py`: LLM interface (`complete(system, user, temperature)`)
- `autoskill/llm/factory.py`: provider factory (`mock|openai|dashscope|glm|anthropic`)
- `autoskill/llm/mock.py`: offline mock LLM (deterministic text response)
- `autoskill/llm/openai.py`: minimal OpenAI-compatible Chat Completions client (used for OpenAI + DashScope)
- `autoskill/llm/glm.py`: BigModel GLM-4.7 Chat Completions client (auth_mode auto/jwt/api_key)
- `autoskill/llm/anthropic.py`: minimal Anthropic Messages client

#### `autoskill/embeddings/` (Embedding Providers)

- `autoskill/embeddings/__init__.py`: provider-layer exports (`EmbeddingModel`, `build_embeddings`)
- `autoskill/embeddings/base.py`: embedding interface (`embed(texts) -> vectors`)
- `autoskill/embeddings/factory.py`: provider factory (`hashing|openai|dashscope|glm`)
- `autoskill/embeddings/hashing.py`: offline hashing embeddings (fast baseline; no network)
- `autoskill/embeddings/openai.py`: minimal OpenAI-compatible embeddings client (used for OpenAI + DashScope)
- `autoskill/embeddings/bigmodel.py`: BigModel embedding-3 client (auth_mode auto/jwt/api_key)

#### `autoskill/skill_management/` (Extraction + Maintenance + Formats)

- `autoskill/skill_management/__init__.py`: skill-management exports (extract/maintain/store/vector helpers)
- `autoskill/skill_management/extraction.py`: Skill extraction (`SkillExtractor`, LLM extraction + repair + heuristic fallback)
- `autoskill/skill_management/maintenance.py`: Skill maintenance (dedupe/merge/versioning; optional LLM decisions)
- `autoskill/skill_management/importer.py`: import external Agent Skill directories (scan `**/SKILL.md`)
- `autoskill/skill_management/artifacts.py`: export/write skill artifacts (`SKILL.md`, directories)

##### `autoskill/skill_management/formats/`

- `autoskill/skill_management/formats/__init__.py`: format exports (render/parse helpers)
- `autoskill/skill_management/formats/agent_skill.py`: Agent Skill artifact format (`SKILL.md` frontmatter + body), rendering/parsing helpers

##### `autoskill/skill_management/stores/`

- `autoskill/skill_management/stores/__init__.py`: store exports (`SkillStore`, `build_store`)
- `autoskill/skill_management/stores/base.py`: `SkillStore` interface
- `autoskill/skill_management/stores/factory.py`: store factory (builds store + per-embedding vector index name)
- `autoskill/skill_management/stores/inmemory.py`: in-memory store (no persistence)
- `autoskill/skill_management/stores/local.py`: filesystem store (one-skill-per-directory; shared `Common/` + user `Users/`; vector cache)

##### `autoskill/skill_management/vectors/`

- `autoskill/skill_management/vectors/__init__.py`: vector-backend exports (`VectorIndex`, `FlatFileVectorIndex`)
- `autoskill/skill_management/vectors/base.py`: vector index interface
- `autoskill/skill_management/vectors/flat.py`: `FlatFileVectorIndex` (exact dot-product search; meta/ids/vecs on disk)

#### `autoskill/interactive/` (Interactive Chat Orchestration)

- `autoskill/interactive/__init__.py`: interactive exports (`InteractiveChatApp`, `InteractiveConfig`, helpers)
- `autoskill/interactive/app.py`: interactive loop orchestration (rewrite → retrieve → respond → extract)
- `autoskill/interactive/config.py`: `InteractiveConfig` (CLI-tunable behavior: scope, thresholds, windows)
- `autoskill/interactive/commands.py`: command parsing (`/help`, `/extract_now`, etc.)
- `autoskill/interactive/io.py`: console IO abstraction (easy to embed in other frontends)
- `autoskill/interactive/rewriting.py`: LLM query rewriting for better skill retrieval
- `autoskill/interactive/selection.py`: optional LLM selector to choose which retrieved skills to inject
- `autoskill/interactive/gating.py`: extraction timing signals (ack/topic-boundary heuristics for when to attempt extraction)

#### `autoskill/utils/` (Shared Utilities)

- `autoskill/utils/__init__.py`: small convenience exports (JSON parsing, redaction, timestamps)
- `autoskill/utils/units.py`: mixed-language sizing + truncation utilities (CJK chars + ASCII words)
- `autoskill/utils/json.py`: fault-tolerant JSON extractor for LLM outputs
- `autoskill/utils/text.py`: keyword extraction (tags + heuristics)
- `autoskill/utils/redact.py`: redaction helpers for source payloads (reduce secret leakage to LLM)
- `autoskill/utils/time.py`: timestamps
- `autoskill/utils/bigmodel_auth.py`: BigModel JWT/auth helpers (used by GLM + embedding-3)

### `examples/` (Runnable Scripts)

- `examples/__init__.py`: examples package entrypoints (run via `python3 -m examples.<script>`)
- `examples/basic_ingest_search.py`: minimal ingest + search demo (offline by default)
- `examples/interactive_chat.py`: interactive loop demo (supports `mock|glm|dashscope|openai|anthropic`)
- `examples/web_ui.py`: local web UI (chat + retrieval/extraction panels)
- `examples/personalized_email_demo.py`: scripted demo of iterative writing → skill extraction → retrieval
- `examples/local_persistent_store.py`: local store demo (skills + vector cache on disk)
- `examples/bigmodel_glm_persistent_store.py`: GLM + embedding-3 with local persistence
- `examples/bigmodel_glm_embed_extract.py`: embed + extract workflow using BigModel providers
- `examples/dashscope_qwen_chat.py`: DashScope chat (OpenAI-compatible) demo
- `examples/dashscope_qwen_embeddings.py`: DashScope embeddings (OpenAI-compatible) demo
- `examples/import_agent_skills.py`: import external Agent Skill directories into a local store
- `examples/normalize_skill_ids.py`: normalize/upsert missing `id:` in `SKILL.md` under a store root

## Examples

See `examples/basic_ingest_search.py`.

Run:

```bash
python3 -m examples.basic_ingest_search
```

Interactive chat (retrieve each turn + optional extract/maintain):

```bash
python3 -m examples.interactive_chat --llm-provider glm
```

Web UI (local) for interactive chat + retrieval/extraction panels:

```bash
python3 -m examples.web_ui --llm-provider glm
```

Then open `http://127.0.0.1:8000` (default). Use Ctrl/Cmd+Enter to send; Enter inserts newline.

Offline personalized email Skill demo (scripted interactive session; no network):

```bash
python3 -m examples.personalized_email_demo
```

Add shared skill libraries (read-only):

- Put downloaded skills under `<store_dir>/Common/...` (either directly as `Common/<skill>/SKILL.md` or grouped as `Common/<library>/<skill>/SKILL.md`), or
- Pass `--library-dir /path/to/skills` (repeatable), or set `AUTOSKILL_LIBRARY_DIRS="/path/a,/path/b"`.

Local persistent store demo (offline):

```bash
python3 -m examples.local_persistent_store
```

BigModel + local persistent store (skills + vectors saved to disk):

```bash
export ZHIPUAI_API_KEY="YOUR_ID.YOUR_SECRET"
python3 -m examples.bigmodel_glm_persistent_store
```

BigModel embed + extract (single script):

```bash
export ZHIPUAI_API_KEY="YOUR_ID.YOUR_SECRET"
python3 -m examples.bigmodel_glm_embed_extract
```

Import existing Agent Skills (directories with `SKILL.md`) into a local store:

```bash
python3 -m examples.import_agent_skills --root-dir /path/to/skills --scope common --store-dir Skills
```

Use the bundled `awesome-claude-skills/` set as a shared library (read-only):

```bash
python3 -m examples.interactive_chat --llm-provider mock --store-dir Skills --library-dir awesome-claude-skills
```

## Interactive Flow (Retrieve + Extract)

In the interactive loop:
- Retrieval runs every user turn before answering (vector search over stored skills).
- Extraction is attempted every N turns in `auto` mode; the extractor decides whether to emit a Skill (or return an empty list) and runs on the next user message so it can include that message as light feedback context.

See `autoskill/interactive/app.py` and `autoskill/interactive/gating.py`.
