# AutoSkill Offline

English | [中文](README.zh-CN.md)

`autoskill.offline` provides batch/offline skill learning workflows for archived data.
Use it when the source data already exists on disk and should be turned into reusable skills without going through the interactive runtime.

## Overview

The offline package currently contains three pipelines:

- `conversation`: extract skills from archived OpenAI-format conversation JSON/JSONL files
- `trajectory`: extract skills from agent execution traces and event logs
- `document`: compile documents into `document -> support record -> skill draft -> skill`, then register versions

All three reuse the existing AutoSkill store and maintenance layer.
They differ in how much intermediate structure they preserve before a skill is produced.

## Overall Flow

```text
offline source
  -> loader / parser
  -> domain-specific offline pipeline
  -> skill maintenance / store update

conversation data
  -> message filtering
  -> direct skill extraction

trajectory data
  -> step / event normalization
  -> direct workflow skill extraction

document data
  -> DocumentRecord
  -> SupportRecord[]
  -> SkillDraft[]
  -> SkillSpec[]
  -> registry + SkillBank/DocSkill
```

The document pipeline is still provenance-aware, but the default path is now skill-first.
It keeps source documents and lightweight support links, instead of forcing a heavy capability compilation step for every corpus.

## Why The Document Pipeline Is Different

For document corpora, the pipeline now keeps four layers separate:

1. `DocumentRecord`
2. `SupportRecord`
3. `SkillDraft`
4. `SkillSpec`

This separation keeps responsibilities clear:

- document: raw input
- support record: traceable support/conflict/constraint/case-variant links from document spans into a skill
- skill draft: extracted candidate skill before reconciliation
- skill: execution output

Versioning is not done by raw `SKILL.md` text diff alone.
It compares normalized skill structure plus support history.

## Current Document Flow

The staged document pipeline lives under [`autoskill/offline/document/`](./document/) and runs:

```text
document
  -> ingest_document
  -> extract_skills
  -> compile_skills
  -> register_versions
  -> registry + SkillBank/DocSkill
```

Current properties:

- incremental ingestion via content hash
- dry-run support
- stage-by-stage rerun support
- provenance links from documents and support records into version changes
- lifecycle-aware versioning: `candidate -> draft -> evaluating -> active -> watchlist -> deprecated -> retired`
- cross-domain design with no psychology-specific schema assumptions

## Document Registry

The document pipeline uses a side-car registry under:

```text
<store_root>/.autoskill/document_registry/
```

It stores first-class records for:

- documents
- supports
- skills
- lifecycles
- version history
- change logs
- provenance links

This registry is the source of truth for offline document compilation history.

## CLI Usage

### 1. Top-level document CLI

The document pipeline is available through the top-level CLI:

```bash
python3 -m autoskill offline document build --file ./paper.md --dry-run
python3 -m autoskill offline document ingest --file ./docs/
python3 -m autoskill offline document extract --file ./paper.md --json
python3 -m autoskill offline document compile --file ./paper.md --json
```

If installed as a script entrypoint:

```bash
autoskill offline document build --file ./paper.md --dry-run
```

### 2. Conversation offline extraction

Conversation extraction currently keeps its module-level CLI:

```bash
python3 -m autoskill.offline.conversation.extract \
  --file ./conversation_logs/ \
  --user-id u1
```

### 3. Trajectory offline extraction

Trajectory extraction also keeps its module-level CLI:

```bash
python3 -m autoskill.offline.trajectory.extract \
  --file ./runs/ \
  --user-id u1
```

## Python API

Programmatic entrypoints stay close to the rest of the repository style:

```python
from autoskill.offline import extract_from_doc

result = extract_from_doc(
    sdk=sdk,
    user_id="u1",
    file_path="./paper.md",
    dry_run=True,
)
```

The document pipeline can also be used stage-by-stage through `DocumentBuildPipeline` when a caller needs to rerun only ingestion, extraction, compilation, or registration.

## Package Layout

```text
autoskill/offline/
  provider_config.py
  conversation/
  trajectory/
  document/
```

Document-specific modules:

- `models.py`: core offline document data models
- `ingest.py`: document normalization and incremental checks
- `extractor.py`: `DocumentRecord -> SupportRecord[] + SkillDraft[]`
- `compiler.py`: `SkillDraft[] -> SkillSpec[]`
- `versioning.py`: skill-centric version and lifecycle management backed by support links
- `registry.py`: side-car persistence for offline document entities
- `pipeline.py`: staged orchestration
- `extract.py`: API + CLI entrypoint

## Extension Points

The document pipeline is intentionally built around replaceable interfaces.

Current extension points:

- `DocumentSkillExtractor`
- `SkillCompiler`
- `VersionManager`

This keeps room for future:

- LLM-backed document skill extraction
- stronger similarity comparators
- offline evaluation and scoring

## Current Scope

What exists now:

- minimal working staged document pipeline
- registry-backed versioning with `create / strengthen / revise / split / merge / deprecate`
- support-backed provenance for each skill update
- CLI access for stage-level debugging and dry runs
- tests for core document paths and versioning scenarios

What is still intentionally lightweight:

- support extraction and reconciliation use clear heuristics first; they are not intended to be final algorithms
- split/merge/deprecate heuristics are simple and clear, not algorithmically heavy
- conversation and trajectory are not yet routed through the top-level `autoskill offline ...` CLI
- LLM extractors, evaluators, and comparators are extension hooks, not the default implementation

## Design Principles

The offline package follows these constraints:

- prefer minimal working implementations first
- keep document/support/skill responsibilities separate
- version using normalized skill structure plus support provenance, not only skill text diffs
- stay domain-agnostic
- reuse existing store, config, prompt runtime, and CLI patterns when possible
