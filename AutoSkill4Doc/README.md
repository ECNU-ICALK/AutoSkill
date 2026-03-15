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
  -> registry + visible parent/child skill tree + optional SkillBank store upsert
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
  <school_name>/
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

## How Parent/Child Skills Are Generated

The current implementation does not try to emit a whole visible skill tree in a
single extraction step. It works in two layers:

1. The document pipeline first produces canonical `SkillSpec` records
   - `ingest` builds `StrictWindow`
   - `extract` produces `SupportRecord + SkillDraft`
   - `compile` turns drafts into `SkillSpec`
   - `register_versions` persists registry state and lifecycle updates

2. The visible parent/child tree is then projected from the current registry state
   - each effective `SkillSpec` becomes one child skill under `子技能/<name>/SKILL.md`
   - `references/evidence.md` and `references/evidence_manifest.json` are built from the linked `SupportRecord + DocumentRecord`
   - one parent navigation skill is synthesized per `school_name`
   - `children_manifest.json` and `children_map.md` are emitted together with the parent skill

This is intentional:

- the source of truth stays in document/support/skill registry layers
- the parent skill remains a navigation layer rather than raw truth
- the visible tree can be rebuilt from registry state after updates

To keep the visible layout stable, the most important flag is:

- `--school-name`

`--profile-id` and `--taxonomy-axis` are also recommended if you want those tags
and manifest fields preserved.

## Is The Flow Reasonable

For the current MVP, yes:

- extraction and visible layout generation are decoupled
- parent/child directories are a projection, not the only truth layer
- rebuilding one school directory from registry state avoids manual drift

But this is still simpler than the full paper target:

- the parent skill is currently synthesized from active child skills
- the visible tree already matches the target directory shape
- the full `single-document standardization + canonical merge + parent synthesis`
  quality pipeline is not fully implemented yet

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
python3 -m AutoSkill4Doc llm-extract --file ./cbt_docs --school-name "认知行为疗法"
python3 -m AutoSkill4Doc ingest --file ./docs/ --json
python3 -m AutoSkill4Doc extract --file ./paper.md --json
autoskill4doc compile --file ./paper.md --json
python3 -m AutoSkill4Doc diag --file ./paper.md --report-path ./diag.jsonl --json
python3 -m AutoSkill4Doc retrieve-hierarchy --store-path ./SkillBank/DocSkill --profile-id test_therapy_v2 --school-name "认知行为疗法" --json
python3 -m AutoSkill4Doc canonical-merge --store-path ./SkillBank/DocSkill --profile-id test_therapy_v2 --school-name "认知行为疗法" --child-type intake --json
python3 -m AutoSkill4Doc migrate-layout --store-path ./SkillBank/DocSkill --json

python3 -m AutoSkill4Doc build \
  --file ./cbt_docs/ \
  --school-name "认知行为疗法" \
  --profile-id test_therapy_v2 \
  --taxonomy-axis "疗法" \
  --store-path ./SkillBank/DocSkill
```

Notes:
- `diag` always runs in non-persisting dry-run mode.
- non-`dry-run` `build` / `llm-extract` writes ingest/extract/compile/register snapshots to `.runtime/intermediate_runs/<run_id>/`.
- `canonical-merge` currently inspects staged results and requires `--profile-id` plus `--school-name`.

## Python API

```python
from AutoSkill4Doc import extract_from_doc

result = extract_from_doc(
    sdk=sdk,
    user_id="u1",
    file_path="./paper.md",
    domain="psychology",
    school_name="认知行为疗法",
    profile_id="test_therapy_v2",
    taxonomy_axis="疗法",
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
- `document/windowing.py`: section filtering and strict/recommended window construction
- `stages/extractor.py`: `DocumentRecord -> SupportRecord[] + SkillDraft[]`
- `stages/compiler.py`: `SkillDraft[] -> SkillSpec[]`
- `stages/diag.py`: dry-run diagnostic reporting over extraction windows
- `stages/hierarchy.py`: manifest-first visible hierarchy browse/search
- `stages/merge.py`: staging-backed canonical merge inspection
- `stages/migrate.py`: safe runtime layout preparation
- `store/versioning.py`: skill-centric version/lifecycle reconciliation
- `store/registry.py`: filesystem registry persistence
- `store/visible_tree.py`: visible `总技能/子技能/references` export
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
