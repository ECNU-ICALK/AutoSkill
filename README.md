# AutoSkill SDK

AutoSkill is a self-evolving "Skill Layer" SDK: it automatically grows reusable, executable **Skills** from
conversations and behavior/event logs, continuously maintains them (dedupe/merge/versioning), and
retrieves/injects the right Skills to improve downstream task performance as you use it.

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

## Provider Config Examples (OpenAI / Anthropic)

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

- LLM: `mock` (offline), `openai`, `anthropic`, `glm` (BigModel GLM-4.7)
- Embeddings: `hashing` (offline), `openai`, `glm` (BigModel embedding-3)
- Store: `inmemory` (offline), `local` (directory-based persistence: `Users/<user_id>/...` + optional shared `Common/...`; caches vectors in a persistent on-disk index for fast retrieval)

## Layout

The `autoskill/` package is the SDK, inspired by Mem0's "client + provider + store" layering.

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
- Extraction is gated to protect quality; when enabled, extraction is deferred until the next user message so it can be used as feedback (worked/didn't work) before ingesting a new Skill.

See `autoskill/interactive/app.py` and `autoskill/interactive/gating.py`.
