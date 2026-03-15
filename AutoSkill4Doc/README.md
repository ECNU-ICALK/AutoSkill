# AutoSkill4Doc

English | [中文](README.zh-CN.md)

`AutoSkill4Doc` is the standalone offline document-to-skill engine for this repository.
It turns documents into executable skills through explicit offline stages, while
keeping provenance, version history, and incremental re-run support.

## Scope

Current pipeline:

```text
document
  -> ingest_document (DocumentRecord + TextUnit + StrictWindow)
  -> extract_skills (SupportRecord + SkillDraft)
  -> compile_skills (SkillSpec)
  -> register_versions
  -> registry + staged snapshots + final SkillBank store + visible parent/child skill tree
```

Core layers:

1. `DocumentRecord`
2. `TextUnit`
3. `StrictWindow`
4. `SupportRecord`
5. `SkillDraft`
6. `SkillSpec`

## Key Features

- standalone CLI: `autoskill4doc ...` or `python -m AutoSkill4Doc ...`
- incremental skip by content hash
- section filtering + dialogue-aware pruning + strict/recommended windowing
- dry-run and stage-by-stage execution
- support-backed provenance and change logs
- lifecycle-aware versioning: `candidate -> draft -> evaluating -> active -> watchlist -> deprecated -> retired`
- visible parent/child output tree under the document skill library root
- incremental intermediate snapshots under `.runtime/intermediate_runs/<run_id>/` during non-dry-run builds
- configurable skill taxonomy via built-in or custom YAML files, with `domain_type` supplied by the caller rather than predicted by the model

Input notes:
- text / markdown / json / jsonl are read directly
- `.doc` / `.docx` require local conversion tools such as `textutil`, `antiword`, or `catdoc`
- unsupported binary files such as images or PDFs are currently skipped rather than decoded as noisy text
- `generic` LLM / embedding backends require explicit `AUTOSKILL_GENERIC_LLM_URL` / `AUTOSKILL_GENERIC_EMBED_URL`
- generated visible-tree artifacts under `总技能/`, `子技能/`, and `references/` are skipped during ingest so exported skills are not re-extracted as source documents

## Default Paths

Default library root:

```text
<repo_root>/SkillBank/DocSkill/
```

Default registry root:

```text
<store_root>/.runtime/document_registry/
```

Default intermediate run root:

```text
<store_root>/.runtime/intermediate_runs/
```

Visible output tree:

```text
<store_root>/
  README.md
  <family_name>/
    总技能/
      SKILL.md
      references/
        children_manifest.json
        children_map.md
    子技能/
      <child_name>/
        SKILL.md
        references/
          evidence.md
          evidence_manifest.json
  .runtime/
    document_registry/
    intermediate_runs/
    staging/
    library_manifest.json
```

Storage layers under the same library root:

1. `.runtime/document_registry/`
   - internal document/support/skill/version records
2. `Users/<internal_user>/`
   - final AutoSkill local-store skills after maintainer reconciliation
3. `<family_name>/`
   - visible parent/child projection built for browsing and export

These layers share one root, but they are not the same dataset. During long runs,
non-`dry-run` builds also write incremental snapshots under
`.runtime/intermediate_runs/<run_id>/`.

## How Parent/Child Skills Are Generated

The current implementation does not try to emit a whole visible skill tree in a
single extraction step. It works in two layers:

1. The document pipeline first produces canonical `SkillSpec` records
   - `ingest` builds `StrictWindow`
   - `extract` produces `SupportRecord + SkillDraft`
   - `compile` turns drafts into `SkillSpec`
   - `register_versions` persists registry state and lifecycle updates

2. The visible parent/child tree is then projected for browsing/export
   - if final store skills are available, the visible child skills are rebuilt from the reconciled `Users/<internal_user>/...` store results
   - registry records are still used to stitch `references/evidence.md` and `references/evidence_manifest.json`
   - one parent navigation skill is synthesized per `family_name`
   - `children_manifest.json` and `children_map.md` are emitted together with the parent skill

This is intentional:

- the source of truth stays in document/support/skill registry layers
- the parent skill remains a navigation layer rather than raw truth
- the visible tree can be rebuilt after updates without manual drift
- the visible family tree now prefers final store-reconciled skills so it stays aligned with `Users/<internal_user>/...`

To keep the visible layout stable, the most important flag is:

- `--family-name`

If `--profile-id` is omitted, AutoSkill4Doc now derives one from the selected
taxonomy plus `family_name`. If `--taxonomy-axis` is omitted, the selected
taxonomy may provide a default axis label.
`--user-id` is now treated as an internal store-routing detail and is no longer
part of the normal documented workflow.

## Skill Taxonomy

`AutoSkill4Doc` keeps a small stable internal `asset_type` set for compile/versioning:

- `macro_protocol`
- `session_skill`
- `micro_skill`
- `safety_rule`
- `knowledge_reference`

On top of that, extraction can load a configurable skill taxonomy:

- built-in via `--domain-type psychology` / `--domain-type chemistry`
- custom via `--skill-taxonomy /path/to/taxonomy.yaml`

Important:

- `domain_type` is caller-provided configuration, not model output
- the model still returns the stable internal `asset_type`
- taxonomy files provide:
  - domain-specific labels, aliases, and guidance
  - optional default `family_name`
  - optional default `taxonomy_axis`
  - optional family candidates for future constrained family resolution

Example:

```bash
python3 -m AutoSkill4Doc llm-extract \
  --file ./chem_docs \
  --domain chemistry \
  --domain-type chemistry \
  --family-name "分析化学" \
  --skill-taxonomy ./custom-taxonomy.yaml \
  --store-path ./SkillBank/DocSkill
```

## Configuration Files

AutoSkill4Doc currently uses three configuration layers:

1. Built-in taxonomy files
   - [AutoSkill4Doc/skill_taxonomies/default.yaml](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/skill_taxonomies/default.yaml)
   - [AutoSkill4Doc/skill_taxonomies/psychology.yaml](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/skill_taxonomies/psychology.yaml)
   - [AutoSkill4Doc/skill_taxonomies/chemistry.yaml](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/skill_taxonomies/chemistry.yaml)
2. One optional user taxonomy file passed via `--skill-taxonomy`
3. Runtime CLI arguments and provider env vars

How taxonomy loading works:

- `default.yaml` is always loaded first
- if `--domain-type psychology` / `chemistry` is set, the matching built-in file is overlaid on top of `default.yaml`
- if `--skill-taxonomy /path/to/file.yaml` is set, that file is used as the overlay instead of the built-in domain file
- the final resolved values then feed:
  - extraction prompt guidance
  - `asset_type` alias normalization
  - default `family_name`
  - default `taxonomy_axis`
  - auto-derived `profile_id`

Important taxonomy fields:

- `taxonomy_id`: stable taxonomy id used when deriving `profile_id`
- `domain_type`: the externally supplied domain type name
- `display_name`: human-readable label
- `default_base_type`: fallback internal `asset_type`
- `family_axis`: default visible axis label, such as `疗法` or `实验路线`
- `default_family_name`: fallback visible family name
- `family_candidates`: optional constrained candidate set for future family resolution
- `asset_types`: domain labels mapped back to stable internal base types

Minimal taxonomy example:

```yaml
taxonomy_id: psychology
domain_type: psychology
display_name: Psychology
default_base_type: session_skill
family_axis: 疗法
default_family_name: 通用心理咨询
family_candidates:
  - id: cbt
    name: CBT（认知行为疗法）
    aliases: ["CBT", "认知行为疗法", "cognitive behavioral therapy"]
asset_types:
  - base_type: session_skill
    label: session_intervention
    description: One counseling workflow or session scaffold.
    aliases: ["session_intervention", "session_skill"]
```

Other configuration sources:

- [AutoSkill4Doc/core/config.py](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/core/config.py)
  - code defaults such as default store path, runtime path, and extract strategy
- [AutoSkill4Doc/core/provider_config.py](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/core/provider_config.py)
  - provider/env resolution for `dashscope`, `glm`, `openai`, `anthropic`, and `generic`

Provider config is environment-variable based rather than file-based. Common examples:

- DashScope: `DASHSCOPE_API_KEY`, optional `DASHSCOPE_MODEL`, `DASHSCOPE_EMBED_MODEL`
- GLM: `ZHIPUAI_API_KEY` or `BIGMODEL_API_KEY`
- Generic backend: `AUTOSKILL_GENERIC_LLM_URL`, `AUTOSKILL_GENERIC_EMBED_URL`

Resolution priority:

- explicit CLI argument
- custom taxonomy file
- built-in taxonomy file
- code default in `core/config.py`
- provider env vars for backend credentials and endpoint URLs

## Is The Flow Reasonable

For the current MVP, yes:

- extraction and visible layout generation are decoupled
- parent/child directories are a projection, not the only truth layer
- rebuilding one family directory from final store output plus registry evidence avoids manual drift

But this is still simpler than the full paper target:

- the parent skill is currently synthesized from active child skills
- the visible tree already matches the target directory shape
- the full `single-document standardization + canonical merge + parent synthesis`
  quality pipeline is not fully implemented yet
- `.runtime/document_registry/` may still contain more internal skill records than
  the final `Users/<internal_user>/...` store and visible `<family_name>/...` tree

Stored entities:

- `documents`
- `supports`
- `skills`
- `lifecycles`
- `version_history`
- `change_logs`
- `provenance_links`

## CLI

Standalone CLI:

```bash
python3 -m AutoSkill4Doc build --file ./paper.md --dry-run
python3 -m AutoSkill4Doc llm-extract --file ./cbt_docs --family-name "认知行为疗法"
python3 -m AutoSkill4Doc ingest --file ./docs/ --json
python3 -m AutoSkill4Doc extract --file ./paper.md --json
autoskill4doc compile --file ./paper.md --json
python3 -m AutoSkill4Doc diag --file ./paper.md --report-path ./diag.jsonl --json
python3 -m AutoSkill4Doc retrieve-hierarchy --store-path ./SkillBank/DocSkill --profile-id psychology::认知行为疗法 --family-name "认知行为疗法" --json
python3 -m AutoSkill4Doc canonical-merge --store-path ./SkillBank/DocSkill --profile-id psychology::认知行为疗法 --family-name "认知行为疗法" --child-type intake --json
python3 -m AutoSkill4Doc migrate-layout --store-path ./SkillBank/DocSkill --json

python3 -m AutoSkill4Doc build \
  --file ./cbt_docs/ \
  --domain psychology \
  --domain-type psychology \
  --family-name "认知行为疗法" \
  --store-path ./SkillBank/DocSkill
```

Notes:
- `dry-run` runs ingest/extract/compile for inspection but does not write final registry/store/visible-tree results.
- `diag` always runs in non-persisting dry-run mode.
- non-`dry-run` `build` / `llm-extract` writes ingest/extract/compile/register snapshots to `.runtime/intermediate_runs/<run_id>/`.
- `canonical-merge` currently inspects staged results and requires `--profile-id` plus `--family-name`.

## Python API

```python
from AutoSkill4Doc import extract_from_doc

result = extract_from_doc(
    sdk=sdk,
    file_path="./paper.md",
    domain="psychology",
    domain_type="psychology",
    family_name="认知行为疗法",
    dry_run=True,
)
```

Stage-level orchestration:

```python
from AutoSkill4Doc.pipeline import build_default_document_pipeline

pipeline = build_default_document_pipeline(sdk=sdk)
ingest = pipeline.ingest_document(file_path="./paper.md", dry_run=True)
print(len(ingest.windows))
extracted = pipeline.extract_skills(documents=ingest.documents, windows=ingest.windows)
compiled = pipeline.compile_skills(
    skill_drafts=extracted.skill_drafts,
    support_records=extracted.support_records,
)
```

## Module Map

- `extract.py` / `__main__.py`: standalone package CLI + API entrypoint
- `pipeline.py`: staged orchestration
- `ingest.py`: document normalization and incremental checks
- `taxonomy.py`: built-in/custom skill taxonomy loading plus `family_name`/`profile_id` resolution
- `document/file_loader.py`: directory/file loading, conversion fallback, and generated-artifact skipping
- `document/windowing.py`: section filtering and strict/recommended window construction
- `stages/extractor.py`: `DocumentRecord -> SupportRecord[] + SkillDraft[]`
- `stages/compiler.py`: `SkillDraft[] -> SkillSpec[]`
- `stages/diag.py`: dry-run diagnostic reporting over extraction windows
- `stages/hierarchy.py`: manifest-first visible hierarchy browse/search
- `stages/merge.py`: staging-backed canonical merge inspection
- `stages/migrate.py`: safe runtime layout preparation
- `store/versioning.py`: skill-centric version/lifecycle reconciliation
- `store/registry.py`: filesystem registry persistence
- `store/visible_tree.py`: visible `总技能/子技能/references` export, rebuilt from final store skills plus registry evidence
- `store/intermediate.py`: incremental per-run ingest/extract/compile/register snapshots
- `store/layout.py`: shared visible/runtime path conventions
- `store/staging.py`: canonical-merge staging payload helpers
- `core/config.py`: standalone AutoSkill4Doc defaults and paths
- `core/provider_config.py`: standalone provider configuration helpers
- `models.py`: core data models
- `prompts.py`: offline prompt builders plus runtime prompt switching

## Notes

- This module replaced the old `autoskill/offline/document/` implementation.
- Document extraction now runs through `AutoSkill4Doc` directly rather than `autoskill/offline`.
- `python -m AutoSkill4Doc` is the recommended module entry; `extract.py` is kept as the implementation module behind that CLI.
