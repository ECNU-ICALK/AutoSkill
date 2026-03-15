"""
Staged offline document pipeline entrypoints.

This module exposes the current staged AutoSkill4Doc command surface.

It keeps:
- `extract_from_doc(...)` remains the programmatic entrypoint
- `main()` exposes a small CLI with stage-oriented commands

Commands:
- `build`: full document -> skill draft -> canonical skill -> registry/store flow
- `llm-extract`: compatibility alias of `build`
- `ingest`: only normalize/import documents and run incremental checks
- `extract`: stop after support record and skill draft extraction
- `compile`: stop after canonical skill compilation without persisting registry/store updates
- `diag`: run ingest + extract in dry-run mode with optional JSONL diagnostics
- `retrieve-hierarchy`: browse/search the visible parent/child skill tree
- `canonical-merge`: inspect the latest staged canonical results for one bucket
- `migrate-layout`: prepare the `.runtime` layout and report legacy directories
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

from autoskill import AutoSkill, AutoSkillConfig

from .core.common import StageLogger
from .core.config import (
    DEFAULT_DOC_SKILL_USER_ID,
    DEFAULT_EXTRACT_STRATEGY,
    DEFAULT_MAX_SECTION_CHARS,
    SUPPORTED_EXTRACT_STRATEGIES,
    SUPPORTED_SECTION_OUTLINE_MODES,
    default_store_path,
    normalize_extract_strategy,
    normalize_section_outline_mode,
)
from .core.provider_config import (
    build_embeddings_config as _build_provider_embeddings_config,
    build_llm_config as _build_provider_llm_config,
)
from .models import DocumentRecord, SkillDraft, SkillSpec, StrictWindow, SupportRecord, VersionState
from .ingest import HeuristicDocumentIngestor
from .pipeline import DocumentBuildPipeline, DocumentBuildResult, build_default_document_pipeline
from .stages.diag import run_document_diag
from .stages.extractor import build_document_skill_extractor
from .stages.hierarchy import retrieve_hierarchy
from .stages.merge import available_merge_child_types, canonical_merge_from_staging
from .stages.migrate import migrate_layout
from .store.staging import list_child_types, resolve_staging_bucket_context
from .taxonomy import SkillTaxonomy, list_builtin_skill_taxonomies, load_skill_taxonomy

_DOCUMENT_CLI_EXAMPLES = (
    "Examples:\n"
    "  python -m AutoSkill4Doc build --file ./paper.md --dry-run\n"
    "  python -m AutoSkill4Doc llm-extract --file ./cbt_docs --family-name '认知行为疗法'\n"
    "  python -m AutoSkill4Doc diag --file ./paper.md --report-path ./diag.jsonl --json\n"
    "  python -m AutoSkill4Doc retrieve-hierarchy --store-path SkillBank/DocSkill --profile-id psychology::认知行为疗法 --family-name '认知行为疗法'\n"
    "  python -m AutoSkill4Doc canonical-merge --store-path SkillBank/DocSkill --family-name '认知行为疗法'\n"
    "  python -m AutoSkill4Doc build --file ./cbt_docs --domain psychology --domain-type psychology --family-name '认知行为疗法'\n"
    "  python -m AutoSkill4Doc extract --file ./docs/ --json\n"
    "  autoskill4doc migrate-layout --store-path SkillBank/DocSkill --json"
)


def _resolve_taxonomy_context(
    *,
    domain: str,
    domain_type: str,
    skill_taxonomy_path: str,
    family_name: str = "",
    profile_id: str = "",
    taxonomy_axis: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> tuple[SkillTaxonomy, str, str, str]:
    """Resolves taxonomy, family name, axis label, and profile id."""

    taxonomy = load_skill_taxonomy(
        domain_type=str(domain_type or domain or "").strip(),
        taxonomy_path=str(skill_taxonomy_path or "").strip(),
    )
    resolved_family = taxonomy.resolve_family_name(
        requested=str(family_name or "").strip(),
        metadata=metadata,
    )
    resolved_axis = taxonomy.resolve_axis_label(requested=str(taxonomy_axis or "").strip())
    resolved_profile_id = taxonomy.derive_profile_id(
        requested=str(profile_id or "").strip(),
        family_name=resolved_family,
    )
    return taxonomy, resolved_family, resolved_axis, resolved_profile_id


def extract_from_doc(
    *,
    sdk: AutoSkill,
    user_id: str = DEFAULT_DOC_SKILL_USER_ID,
    data: Optional[Any] = None,
    file_path: str = "",
    title: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    hint: Optional[str] = None,
    continue_on_error: bool = True,
    max_chars_per_chunk: int = 6000,
    overlap_chars: int = 300,
    domain: str = "",
    source_type: str = "document",
    registry_root: str = "",
    extract_strategy: str = DEFAULT_EXTRACT_STRATEGY,
    dry_run: bool = False,
    target_state: Optional[VersionState] = None,
    logger: StageLogger = None,
    max_documents: int = 0,
    max_candidates_per_unit: int = 3,
    max_units_per_document: int = 0,
    max_section_chars: int = DEFAULT_MAX_SECTION_CHARS,
    section_outline_mode: str = "auto",
    family_name: str = "",
    profile_id: str = "",
    taxonomy_axis: str = "",
    domain_type: str = "",
    skill_taxonomy_path: str = "",
) -> Dict[str, Any]:
    """
    Runs the staged offline document pipeline and returns a compact summary.

    `extract_strategy` controls how ingestion prepares local extraction windows:
    - `recommended`: current default, normalized to strict window planning
    - `strict`: explicit strict window planning
    - `chunk`: fallback chunk-style windows for broader coverage
    """

    md = dict(metadata or {})
    md.setdefault("channel", "offline_extract_from_doc")
    md.setdefault("source_type", str(source_type or "").strip() or "document")
    if hint and str(hint).strip():
        md.setdefault("hint", str(hint).strip())
    taxonomy, resolved_family, resolved_axis, resolved_profile_id = _resolve_taxonomy_context(
        domain=domain,
        domain_type=domain_type,
        skill_taxonomy_path=skill_taxonomy_path,
        family_name=family_name,
        profile_id=profile_id,
        taxonomy_axis=taxonomy_axis,
        metadata=md,
    )
    if resolved_family:
        md["family_name"] = resolved_family
    if resolved_profile_id:
        md["profile_id"] = resolved_profile_id
    if resolved_axis:
        md["taxonomy_axis"] = resolved_axis
    if str(domain_type or domain or "").strip():
        md["domain_type"] = str(domain_type or domain).strip()

    pipeline = build_default_document_pipeline(
        sdk=sdk,
        registry_root=str(registry_root or "").strip(),
        logger=logger,
        document_ingestor=HeuristicDocumentIngestor(
            llm_config=dict(getattr(getattr(sdk, "config", None), "llm", {}) or {}),
            max_section_chars=int(max_section_chars or 0) or DEFAULT_MAX_SECTION_CHARS,
            outline_fallback_mode=normalize_section_outline_mode(section_outline_mode),
        ),
        document_skill_extractor=build_document_skill_extractor(
            "llm",
            llm_config=dict(getattr(getattr(sdk, "config", None), "llm", {}) or {}),
            max_section_chars=int(max_chars_per_chunk or 0) or 6000,
            overlap_chars=int(overlap_chars or 0),
            max_candidates_per_unit=int(max_candidates_per_unit or 0) or 3,
            max_units_per_document=int(max_units_per_document or 0),
            domain_type=taxonomy.domain_type,
            skill_taxonomy_path=str(skill_taxonomy_path or "").strip(),
            taxonomy=taxonomy,
        ),
    )
    result = pipeline.build(
        user_id=str(user_id or "").strip() or DEFAULT_DOC_SKILL_USER_ID,
        data=data,
        file_path=str(file_path or "").strip(),
        title=str(title or "").strip(),
        source_type=str(source_type or "").strip() or "document",
        domain=str(domain or "").strip(),
        metadata=md,
        continue_on_error=bool(continue_on_error),
        dry_run=bool(dry_run),
        target_state=target_state,
        max_documents=int(max_documents or 0),
        extract_strategy=normalize_extract_strategy(extract_strategy),
    )
    return _build_summary(pipeline=pipeline, result=result)


def _plain_document(record: DocumentRecord) -> Dict[str, Any]:
    """Serializes one DocumentRecord into a compact summary."""

    return {
        "doc_id": record.doc_id,
        "title": record.title,
        "source_type": record.source_type,
        "domain": record.domain,
        "content_hash": record.content_hash,
        "section_count": len(record.sections or []),
    }


def _plain_support(record: SupportRecord) -> Dict[str, Any]:
    """Serializes one SupportRecord into a compact summary."""

    return {
        "support_id": record.support_id,
        "doc_id": record.doc_id,
        "skill_id": record.skill_id,
        "section": record.section,
        "relation_type": record.relation_type.value,
        "confidence": record.confidence,
        "excerpt": record.excerpt,
    }


def _plain_window(window: StrictWindow) -> Dict[str, Any]:
    """Serializes one strict/recommended window into a compact summary."""

    return {
        "window_id": window.window_id,
        "doc_id": window.doc_id,
        "section_heading": window.section_heading,
        "paragraph_start": window.paragraph_start,
        "paragraph_end": window.paragraph_end,
        "anchor_hits": list(window.anchor_hits or []),
        "strategy": window.strategy,
        "text": window.text,
    }


def _plain_draft(draft: SkillDraft) -> Dict[str, Any]:
    """Serializes one SkillDraft into a compact summary."""

    return {
        "draft_id": draft.draft_id,
        "doc_id": draft.doc_id,
        "name": draft.name,
        "asset_type": draft.asset_type,
        "granularity": draft.granularity,
        "objective": draft.objective,
        "domain": draft.domain,
        "task_family": draft.task_family,
        "method_family": draft.method_family,
        "stage": draft.stage,
        "risk_class": draft.risk_class,
        "support_ids": list(draft.support_ids or []),
    }


def _plain_skill_spec(spec: SkillSpec) -> Dict[str, Any]:
    """Serializes one SkillSpec into a compact CLI/API summary."""

    return {
        "skill_id": spec.skill_id,
        "name": spec.name,
        "description": spec.description,
        "asset_type": spec.asset_type,
        "granularity": spec.granularity,
        "objective": spec.objective,
        "domain": spec.domain,
        "task_family": spec.task_family,
        "method_family": spec.method_family,
        "stage": spec.stage,
        "version": spec.version,
        "status": spec.status.value,
        "support_ids": list(spec.support_ids or []),
    }


def _build_summary(*, pipeline: DocumentBuildPipeline, result: DocumentBuildResult) -> Dict[str, Any]:
    """Builds a stable plain-dict response from a DocumentBuildResult."""

    skills_out: List[Dict[str, Any]]
    if result.registration.upserted_store_skills:
        skills_out = list(result.registration.upserted_store_skills)
    else:
        skills_out = [_plain_skill_spec(spec) for spec in list(result.registration.skill_specs or [])]

    errors = (
        list(result.ingest.errors)
        + list(result.extracted.errors)
        + list(result.compiled.errors)
        + list(result.registration.errors)
    )
    total_units = len(result.ingest.documents) + len(result.ingest.skipped_documents)
    return {
        "dry_run": bool(result.dry_run),
        "registry_root": pipeline.registry.root_dir,
        "source_file": result.ingest.source_file,
        "total_units": total_units,
        "total_documents": len(result.ingest.documents),
        "skipped_documents": len(result.ingest.skipped_documents),
        "total_windows": len(result.ingest.windows),
        "total_support_records": len(result.extracted.support_records),
        "total_skill_drafts": len(result.extracted.skill_drafts),
        "total_skill_specs": len(result.compiled.skill_specs),
        "lifecycle_events": len(result.registration.lifecycles),
        "change_events": len(result.registration.change_logs),
        "version_history_entries": len(result.registration.version_history),
        "provenance_links": len(result.registration.provenance_links),
        "upserted_count": len(result.registration.upserted_store_skills),
        "staging_runs": list(result.registration.staging_runs or []),
        "visible_tree": dict(result.registration.visible_tree or {}),
        "intermediate": dict(result.intermediate or {}),
        "skills": skills_out,
        "errors": errors,
    }


def _build_llm_config(args: argparse.Namespace) -> Dict[str, Any]:
    """Builds the LLM provider config from CLI args."""

    provider = str(args.llm_provider or "mock").strip() or "mock"
    model = str(args.llm_model or "").strip() or None
    cfg = _build_provider_llm_config(provider, model=model)
    if str(args.llm_base_url or "").strip():
        cfg["base_url"] = str(args.llm_base_url).strip()
    if str(args.llm_api_key or "").strip():
        cfg["api_key"] = str(args.llm_api_key).strip()
    if str(args.auth_mode or "").strip():
        cfg["auth_mode"] = str(args.auth_mode).strip()
    if str(getattr(args, "llm_response", "") or "").strip():
        raw = str(args.llm_response).strip()
        try:
            cfg["response"] = json.loads(raw)
        except Exception:
            cfg["response"] = raw
    return cfg


def _build_embeddings_config(args: argparse.Namespace) -> Dict[str, Any]:
    """Builds the embeddings provider config from CLI args."""

    llm_provider = str(args.llm_provider or "mock").strip().lower() or "mock"
    provider = str(args.embeddings_provider or "").strip()
    model = str(args.embeddings_model or "").strip() or None
    cfg = _build_provider_embeddings_config(provider, model=model, llm_provider=llm_provider)
    if str(args.embeddings_base_url or "").strip():
        cfg["base_url"] = str(args.embeddings_base_url).strip()
    if str(args.embeddings_api_key or "").strip():
        cfg["api_key"] = str(args.embeddings_api_key).strip()
    if str(args.embeddings_auth_mode or "").strip():
        cfg["auth_mode"] = str(args.embeddings_auth_mode).strip()
    dims = int(args.embeddings_dims or 0)
    provider_norm = str(cfg.get("provider") or "").strip().lower()
    if provider_norm == "hashing":
        cfg["dims"] = int(dims) if dims > 0 else 256
    elif dims > 0 and provider_norm != "none":
        cfg["dimensions"] = int(dims)
        cfg["extra_body"] = {"dimensions": int(dims)}
    return cfg


def _build_sdk_from_args(args: argparse.Namespace) -> AutoSkill:
    """Builds an AutoSkill SDK for document pipeline commands."""

    llm_cfg = _build_llm_config(args)
    emb_cfg = _build_embeddings_config(args)
    store_cfg: Dict[str, Any] = {
        "provider": "local",
        "path": str(args.store_path or "").strip() or default_store_path(),
    }
    return AutoSkill(
        AutoSkillConfig(
            llm=llm_cfg,
            embeddings=emb_cfg,
            store=store_cfg,
            maintenance_strategy="heuristic" if str(args.maintenance_strategy or "").strip() == "heuristic" else "llm",
        )
    )


def _coerce_state(value: str, *, default: VersionState) -> VersionState:
    """Parses a CLI lifecycle state into VersionState."""

    raw = str(value or "").strip().lower()
    if not raw:
        return default
    return VersionState(raw)


def _build_pipeline_from_args(args: argparse.Namespace) -> DocumentBuildPipeline:
    """Constructs the default document pipeline for CLI commands."""

    sdk = _build_sdk_from_args(args)
    taxonomy, _, _, _ = _resolve_taxonomy_context(
        domain=str(getattr(args, "domain", "") or "").strip(),
        domain_type=str(getattr(args, "domain_type", "") or "").strip(),
        skill_taxonomy_path=str(getattr(args, "skill_taxonomy", "") or "").strip(),
        family_name=str(getattr(args, "family_name", "") or "").strip(),
        profile_id=str(getattr(args, "profile_id", "") or "").strip(),
        taxonomy_axis=str(getattr(args, "taxonomy_axis", "") or "").strip(),
    )
    return build_default_document_pipeline(
        sdk=sdk,
        registry_root=str(args.registry_root or "").strip(),
        logger=(None if bool(args.quiet) else print),
        document_ingestor=HeuristicDocumentIngestor(
            llm_config=dict(getattr(getattr(sdk, "config", None), "llm", {}) or {}),
            max_section_chars=int(getattr(args, "max_section_chars", 0) or 0) or DEFAULT_MAX_SECTION_CHARS,
            outline_fallback_mode=normalize_section_outline_mode(str(getattr(args, "section_outline_mode", "") or "auto")),
        ),
        document_skill_extractor=build_document_skill_extractor(
            "llm",
            llm_config=dict(getattr(getattr(sdk, "config", None), "llm", {}) or {}),
            max_section_chars=int(args.max_chars_per_chunk or 0) or 6000,
            overlap_chars=int(args.overlap_chars or 0),
            max_candidates_per_unit=int(args.max_candidates_per_unit or 0) or 3,
            max_units_per_document=int(args.max_units_per_document or 0),
            domain_type=taxonomy.domain_type,
            skill_taxonomy_path=str(getattr(args, "skill_taxonomy", "") or "").strip(),
            taxonomy=taxonomy,
        ),
    )


def _base_metadata(args: argparse.Namespace) -> Dict[str, Any]:
    """Builds common metadata shared across CLI commands."""

    md = {"channel": "offline_extract_from_doc", "source_type": str(args.source_type or "").strip() or "document"}
    if str(args.hint or "").strip():
        md["hint"] = str(args.hint).strip()
    _, resolved_family, resolved_axis, resolved_profile_id = _resolve_taxonomy_context(
        domain=str(getattr(args, "domain", "") or "").strip(),
        domain_type=str(getattr(args, "domain_type", "") or "").strip(),
        skill_taxonomy_path=str(getattr(args, "skill_taxonomy", "") or "").strip(),
        family_name=str(getattr(args, "family_name", "") or "").strip(),
        profile_id=str(getattr(args, "profile_id", "") or "").strip(),
        taxonomy_axis=str(getattr(args, "taxonomy_axis", "") or "").strip(),
        metadata=md,
    )
    if resolved_family:
        md["family_name"] = resolved_family
    if resolved_profile_id:
        md["profile_id"] = resolved_profile_id
    if resolved_axis:
        md["taxonomy_axis"] = resolved_axis
    if str(getattr(args, "domain_type", "") or getattr(args, "domain", "") or "").strip():
        md["domain_type"] = str(getattr(args, "domain_type", "") or getattr(args, "domain", "")).strip()
    return md


def _ingest_for_cli(
    pipeline: DocumentBuildPipeline,
    args: argparse.Namespace,
    *,
    dry_run: bool,
):
    """Runs the shared ingest stage for CLI subcommands."""

    return pipeline.ingest_document(
        file_path=str(args.file or "").strip(),
        title=str(args.title or "").strip(),
        source_type=str(args.source_type or "").strip() or "document",
        domain=str(args.domain or "").strip(),
        metadata=_base_metadata(args),
        continue_on_error=bool(args.continue_on_error),
        dry_run=bool(dry_run),
        max_documents=int(args.max_documents or 0),
        extract_strategy=normalize_extract_strategy(args.extract_strategy),
    )


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Adds shared document CLI arguments."""

    parser.add_argument("--file", default="", help="Single file or directory containing offline documents.")
    parser.add_argument("--title", default="", help="Optional document title override for inline input.")
    parser.add_argument("--domain", default="", help="Optional domain hint, e.g. psychology or chemistry.")
    parser.add_argument(
        "--domain-type",
        default="",
        help="Selected taxonomy domain type. This is user-provided configuration rather than model output.",
    )
    parser.add_argument(
        "--skill-taxonomy",
        default="",
        help=f"Optional custom skill taxonomy YAML path. Built-ins: {', '.join(list_builtin_skill_taxonomies())}.",
    )
    parser.add_argument("--source-type", default="document", help="Generic source type label stored with imported documents.")
    parser.add_argument(
        "--extract-strategy",
        default=DEFAULT_EXTRACT_STRATEGY,
        choices=list(SUPPORTED_EXTRACT_STRATEGIES),
        help="Window planning strategy used during ingest. `recommended` currently resolves to strict windows.",
    )
    parser.add_argument(
        "--registry-root",
        default="",
        help="Override the document registry root. Default: <store>/.runtime/document_registry.",
    )
    parser.add_argument(
        "--store-path",
        default="",
        help="AutoSkill4Doc store path. Default: <repo_root>/SkillBank/DocSkill.",
    )
    parser.add_argument("--user-id", default=DEFAULT_DOC_SKILL_USER_ID, help=argparse.SUPPRESS)
    parser.add_argument("--hint", default="", help="Optional extraction hint stored in metadata.")
    parser.add_argument(
        "--family-name",
        default="",
        help="Optional visible family name used for the exported parent/child skill tree, e.g. 认知行为疗法.",
    )
    parser.add_argument(
        "--profile-id",
        default="",
        help="Optional profile id recorded into visible skill tags and manifests. If omitted, one is derived from taxonomy + family_name.",
    )
    parser.add_argument(
        "--taxonomy-axis",
        default="",
        help="Optional family axis label recorded into visible skill tags and manifests. If omitted, the selected taxonomy may provide a default.",
    )
    parser.set_defaults(continue_on_error=True)
    parser.add_argument(
        "--continue-on-error",
        dest="continue_on_error",
        action="store_true",
        help="Continue processing remaining documents after one document fails. This is the default.",
    )
    parser.add_argument(
        "--fail-fast",
        dest="continue_on_error",
        action="store_false",
        help="Stop immediately on the first document error.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without persisting registry or store changes where applicable.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    parser.add_argument("--quiet", action="store_true", help="Suppress stage logs and only print final output.")
    parser.add_argument("--max-documents", type=int, default=0, help="Limit how many files are read when --file points to a directory. 0 means no limit.")

    parser.add_argument("--llm-provider", default="mock", help="LLM provider id used by AutoSkill4Doc.")
    parser.add_argument("--llm-model", default="", help="LLM model id.")
    parser.add_argument("--llm-base-url", default="", help="Optional LLM base URL.")
    parser.add_argument("--llm-api-key", default="", help=argparse.SUPPRESS)
    parser.add_argument("--auth-mode", default="", help=argparse.SUPPRESS)
    parser.add_argument("--llm-response", default="", help=argparse.SUPPRESS)

    parser.add_argument("--embeddings-provider", default="", help="Embeddings provider id.")
    parser.add_argument("--embeddings-model", default="", help="Embeddings model id.")
    parser.add_argument("--embeddings-base-url", default="", help="Optional embeddings base URL.")
    parser.add_argument("--embeddings-api-key", default="", help=argparse.SUPPRESS)
    parser.add_argument("--embeddings-auth-mode", default="", help=argparse.SUPPRESS)
    parser.add_argument("--embeddings-dims", type=int, default=256, help="Embedding dimensions for hashing/mock providers.")
    parser.add_argument("--maintenance-strategy", default="llm", choices=["heuristic", "llm"], help="Store maintenance strategy.")
    parser.add_argument(
        "--max-section-chars",
        type=int,
        default=DEFAULT_MAX_SECTION_CHARS,
        help="If one detected section is longer than this many characters, pre-split it before final extraction windows are built.",
    )
    parser.add_argument(
        "--section-outline-mode",
        default="auto",
        choices=list(SUPPORTED_SECTION_OUTLINE_MODES),
        help="How to recover section/subsection hierarchy when rule-based heading detection fails. `auto` allows one outline LLM pass per document; `off` disables it.",
    )

    parser.add_argument(
        "--max-chars-per-chunk",
        "--max-chars-per-window",
        type=int,
        default=6000,
        help="Maximum characters per extraction window/unit. Short sections stay whole; long sections fall back to smaller windows.",
    )
    parser.add_argument(
        "--overlap-chars",
        "--window-overlap-chars",
        type=int,
        default=300,
        help="Overlap used when a long section/window must be split into fallback units.",
    )
    parser.add_argument(
        "--max-candidates-per-unit",
        "--max-candidates-per-window",
        type=int,
        default=3,
        help="Maximum skill candidates requested from the model for each extraction window/unit.",
    )
    parser.add_argument(
        "--max-units-per-document",
        "--max-windows-per-document",
        type=int,
        default=0,
        help="Limit how many extraction windows/units are sent to the model per document. 0 means no limit.",
    )


def build_parser() -> argparse.ArgumentParser:
    """Builds the document pipeline CLI parser."""

    parser = argparse.ArgumentParser(
        description="Run the standalone AutoSkill4Doc document pipeline.",
        epilog=_DOCUMENT_CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser(
        "build",
        help="Run the full document -> skill -> registry/store pipeline.",
        description="Read documents, extract support-backed skill drafts, compile canonical skills, and register versions.",
        epilog=_DOCUMENT_CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _add_common_args(build_parser)
    build_parser.add_argument(
        "--target-state",
        default=VersionState.ACTIVE.value,
        choices=[state.value for state in VersionState],
        help="Lifecycle state to assign to newly registered skills.",
    )

    llm_extract_parser = subparsers.add_parser(
        "llm-extract",
        help="Compatibility alias of `build` for the document LLM extraction flow.",
        description="Run the full document pipeline and persist registry/store updates unless --dry-run is set.",
        epilog=_DOCUMENT_CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _add_common_args(llm_extract_parser)
    llm_extract_parser.add_argument(
        "--target-state",
        default=VersionState.ACTIVE.value,
        choices=[state.value for state in VersionState],
        help="Lifecycle state to assign to newly registered skills.",
    )

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Read documents and run incremental checks only.",
        description="Read documents and return normalized DocumentRecord objects without skill extraction.",
    )
    _add_common_args(ingest_parser)

    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract support records and skill drafts.",
        description="Read documents and extract SupportRecord and SkillDraft objects without canonical version registration.",
    )
    _add_common_args(extract_parser)

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile canonical skill specs without persisting them.",
        description="Read documents, extract support-backed drafts, and compile canonical SkillSpec records.",
        epilog=_DOCUMENT_CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _add_common_args(compile_parser)
    compile_parser.add_argument(
        "--target-state",
        default=VersionState.DRAFT.value,
        choices=[state.value for state in VersionState],
        help="Lifecycle state to assign to compiled skill specs.",
    )

    diag_parser = subparsers.add_parser(
        "diag",
        help="Run ingest + extract in diagnostic dry-run mode.",
        description="Inspect extraction windows, supports, and drafts without persisting registry or store changes.",
        epilog=_DOCUMENT_CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _add_common_args(diag_parser)
    diag_parser.add_argument("--report-path", default="", help="Optional JSONL output path for one-row-per-window diagnostics.")
    diag_parser.add_argument("--report-limit", type=int, default=0, help="Optional maximum number of rows to write into --report-path. 0 means no limit.")

    retrieve_parser = subparsers.add_parser(
        "retrieve-hierarchy",
        help="Browse or search the visible parent/child skill hierarchy.",
        description="Use manifest -> visible scan -> runtime registry fallback to browse or search one document skill library.",
        epilog=_DOCUMENT_CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    retrieve_parser.add_argument("--store-path", default="", help="Document skill library root. Default: <repo_root>/SkillBank/DocSkill.")
    retrieve_parser.add_argument("--profile-id", default="", help="Optional profile id used to filter the hierarchy manifest.")
    retrieve_parser.add_argument(
        "--family-name",
        default="",
        help="Optional family name used to browse one subtree.",
    )
    retrieve_parser.add_argument("--query", default="", help="Optional query used to search child skills inside one family.")
    retrieve_parser.add_argument("--limit", type=int, default=20, help="Maximum number of returned child hits.")
    retrieve_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")

    merge_parser = subparsers.add_parser(
        "canonical-merge",
        help="Inspect the latest staged canonical results for one bucket.",
        description="Load the most recent staging payloads written during document registration for one profile/family/child-type bucket. When staging contains one unique bucket, omitted identifiers are inferred automatically.",
        epilog=_DOCUMENT_CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    merge_parser.add_argument("--store-path", default="", help="Document skill library root. Default: <repo_root>/SkillBank/DocSkill.")
    merge_parser.add_argument("--profile-id", default="", help="Optional profile id for the staged canonical bucket. Inferred automatically when staging has one unique match.")
    merge_parser.add_argument(
        "--family-name",
        default="",
        help="Optional visible family name for the staged canonical bucket. Inferred automatically when staging has one unique match.",
    )
    merge_parser.add_argument("--child-type", default="", help="Optional child skill type for the staged canonical bucket.")
    merge_parser.add_argument("--run-id", default="", help="Optional staging run id. Defaults to the latest run in the bucket.")
    merge_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")

    migrate_parser = subparsers.add_parser(
        "migrate-layout",
        help="Prepare `.runtime` layout and report legacy directories.",
        description="Create the expected runtime directories for AutoSkill4Doc and report legacy locations that may need manual migration.",
        epilog=_DOCUMENT_CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    migrate_parser.add_argument("--store-path", default="", help="Document skill library root. Default: <repo_root>/SkillBank/DocSkill.")
    migrate_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")

    return parser


def _print_json(payload: Dict[str, Any]) -> None:
    """Prints one JSON payload to stdout."""

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False))


def _print_errors(errors: List[Dict[str, Any]]) -> None:
    """Prints stage errors in a compact form."""

    if not errors:
        return
    print("Errors:")
    for item in list(errors or []):
        print(f"- {json.dumps(item, ensure_ascii=False, sort_keys=True)}")


def _run_build(args: argparse.Namespace) -> None:
    """Runs the full document build flow."""

    pipeline = _build_pipeline_from_args(args)
    result = pipeline.build(
        user_id=str(args.user_id or "").strip() or DEFAULT_DOC_SKILL_USER_ID,
        file_path=str(args.file or "").strip(),
        title=str(args.title or "").strip(),
        source_type=str(args.source_type or "").strip() or "document",
        domain=str(args.domain or "").strip(),
        metadata=_base_metadata(args),
        continue_on_error=bool(args.continue_on_error),
        dry_run=bool(args.dry_run),
        target_state=_coerce_state(str(args.target_state or ""), default=VersionState.ACTIVE),
        max_documents=int(args.max_documents or 0),
        extract_strategy=normalize_extract_strategy(args.extract_strategy),
    )
    payload = _build_summary(pipeline=pipeline, result=result)
    if bool(args.json):
        _print_json(payload)
        return
    print("Offline document build completed.")
    print(
        f"documents={payload['total_documents']} "
        f"skipped={payload['skipped_documents']} "
        f"windows={payload['total_windows']} "
        f"supports={payload['total_support_records']} "
        f"drafts={payload['total_skill_drafts']} "
        f"skills={payload['total_skill_specs']} "
        f"changes={payload['change_events']} "
        f"staging={len(list(payload.get('staging_runs') or []))} "
        f"families={len(list((payload.get('visible_tree') or {}).get('affected_families') or []))} "
        f"intermediate={'1' if (payload.get('intermediate') or {}).get('run_dir') else '0'}"
    )
    if (payload.get("intermediate") or {}).get("run_dir"):
        print(f"intermediate_run={(payload.get('intermediate') or {}).get('run_dir')}")
    for idx, skill in enumerate(list(payload.get("skills") or [])[:20], start=1):
        print(f"{idx}. {skill.get('name', '')} ({skill.get('version', '')}, {skill.get('status', '')})")
    _print_errors(list(payload.get("errors") or []))


def _run_ingest(args: argparse.Namespace) -> None:
    """Runs only the ingestion stage."""

    pipeline = _build_pipeline_from_args(args)
    result = _ingest_for_cli(pipeline, args, dry_run=bool(args.dry_run))
    payload = {
        "text_units": [unit.to_dict() for unit in list(result.text_units or [])],
        "documents": [_plain_document(doc) for doc in list(result.documents or [])],
        "skipped_documents": [_plain_document(doc) for doc in list(result.skipped_documents or [])],
        "windows": [_plain_window(window) for window in list(result.windows or [])],
        "errors": list(result.errors or []),
    }
    if bool(args.json):
        _print_json(payload)
        return
    print("Offline document ingest completed.")
    print(
        f"documents={len(result.documents)} "
        f"skipped={len(result.skipped_documents)} "
        f"text_units={len(result.text_units)} "
        f"windows={len(result.windows)}"
    )
    _print_errors(list(result.errors or []))


def _run_extract(args: argparse.Namespace) -> None:
    """Runs through direct skill extraction only."""

    pipeline = _build_pipeline_from_args(args)
    ingest_result = _ingest_for_cli(pipeline, args, dry_run=bool(args.dry_run))
    extracted_result = pipeline.extract_skills(documents=ingest_result.documents, windows=ingest_result.windows)
    payload = {
        "documents": [_plain_document(doc) for doc in list(ingest_result.documents or [])],
        "skipped_documents": [_plain_document(doc) for doc in list(ingest_result.skipped_documents or [])],
        "windows": [_plain_window(window) for window in list(ingest_result.windows or [])],
        "support_records": [_plain_support(record) for record in list(extracted_result.support_records or [])],
        "skill_drafts": [_plain_draft(draft) for draft in list(extracted_result.skill_drafts or [])],
        "errors": list(ingest_result.errors) + list(extracted_result.errors),
    }
    if bool(args.json):
        _print_json(payload)
        return
    print("Offline document extract completed.")
    print(
        f"documents={len(ingest_result.documents)} "
        f"skipped={len(ingest_result.skipped_documents)} "
        f"windows={len(ingest_result.windows)} "
        f"supports={len(extracted_result.support_records)} "
        f"drafts={len(extracted_result.skill_drafts)}"
    )
    _print_errors(list(payload.get("errors") or []))


def _run_compile(args: argparse.Namespace) -> None:
    """Runs through canonical skill compilation without registry writes."""

    pipeline = _build_pipeline_from_args(args)
    ingest_result = _ingest_for_cli(pipeline, args, dry_run=True)
    extracted_result = pipeline.extract_skills(documents=ingest_result.documents, windows=ingest_result.windows)
    compiled_result = pipeline.compile_skills(
        skill_drafts=extracted_result.skill_drafts,
        support_records=extracted_result.support_records,
        target_state=_coerce_state(str(args.target_state or ""), default=VersionState.DRAFT),
    )
    payload = {
        "documents": [_plain_document(doc) for doc in list(ingest_result.documents or [])],
        "skipped_documents": [_plain_document(doc) for doc in list(ingest_result.skipped_documents or [])],
        "windows": [_plain_window(window) for window in list(ingest_result.windows or [])],
        "support_records": [_plain_support(record) for record in list(compiled_result.support_records or [])],
        "skill_drafts": [_plain_draft(draft) for draft in list(compiled_result.skill_drafts or [])],
        "skills": [_plain_skill_spec(spec) for spec in list(compiled_result.skill_specs or [])],
        "errors": list(ingest_result.errors) + list(extracted_result.errors) + list(compiled_result.errors),
    }
    if bool(args.json):
        _print_json(payload)
        return
    print("Offline document compile completed.")
    print(
        f"documents={len(ingest_result.documents)} "
        f"skipped={len(ingest_result.skipped_documents)} "
        f"windows={len(ingest_result.windows)} "
        f"supports={len(compiled_result.support_records)} "
        f"drafts={len(compiled_result.skill_drafts)} "
        f"skills={len(compiled_result.skill_specs)}"
    )
    for idx, spec in enumerate(list(compiled_result.skill_specs or [])[:20], start=1):
        print(f"{idx}. {spec.name} ({spec.version}, {spec.status.value})")
    _print_errors(list(payload.get("errors") or []))


def _run_diag(args: argparse.Namespace) -> None:
    """Runs the non-persisting diagnostic extract flow."""

    pipeline = _build_pipeline_from_args(args)
    payload = run_document_diag(
        pipeline=pipeline,
        file_path=str(args.file or "").strip(),
        title=str(args.title or "").strip(),
        source_type=str(args.source_type or "").strip() or "document",
        domain=str(args.domain or "").strip(),
        metadata=_base_metadata(args),
        continue_on_error=bool(args.continue_on_error),
        max_documents=int(args.max_documents or 0),
        extract_strategy=normalize_extract_strategy(args.extract_strategy),
        report_path=str(args.report_path or "").strip(),
        report_limit=int(args.report_limit or 0),
    )
    if bool(args.json):
        _print_json(payload)
        return
    print("Offline document diag completed.")
    print(
        f"documents={payload['documents']} "
        f"skipped={payload['skipped_documents']} "
        f"windows={payload['total_windows']} "
        f"supports={payload['total_support_records']} "
        f"drafts={payload['total_skill_drafts']}"
    )
    if payload.get("report_path"):
        print(f"report={payload['report_path']}")
    _print_errors(list(payload.get("errors") or []))


def _run_retrieve_hierarchy(args: argparse.Namespace) -> None:
    """Browses or searches the visible parent/child hierarchy."""

    payload = retrieve_hierarchy(
        store_root=str(args.store_path or "").strip() or default_store_path(),
        profile_id=str(args.profile_id or "").strip(),
        family_name=str(getattr(args, "family_name", "") or "").strip(),
        query=str(args.query or "").strip(),
        limit=int(args.limit or 20),
    )
    if bool(args.json):
        _print_json(payload)
        return
    route = str(payload.get("route") or "retrieve_hierarchy")
    print(f"Hierarchy route={route}")
    if payload.get("family_name"):
        print(f"family={payload['family_name']}")
    parent = dict(payload.get("parent") or {})
    if parent.get("relative_path"):
        print(f"parent={parent.get('relative_path')}")
    hits = list(payload.get("hits") or [])
    families = list(payload.get("families") or [])
    if families:
        for idx, family in enumerate(families[: int(args.limit or 20)], start=1):
            print(f"{idx}. {family.get('family_name')} ({family.get('child_count', 0)} children)")
    else:
        for idx, hit in enumerate(hits, start=1):
            print(f"{idx}. {hit.get('name', '')} -> {hit.get('relative_path', '')}")
    _print_errors(list(payload.get("errors") or []))


def _run_canonical_merge(args: argparse.Namespace) -> None:
    """Loads the latest staged canonical results for one bucket."""

    store_root = str(args.store_path or "").strip() or default_store_path()
    resolved = resolve_staging_bucket_context(
        base_store_root=store_root,
        profile_id=str(args.profile_id or "").strip(),
        family_id=str(getattr(args, "family_name", "") or "").strip(),
        child_type=str(args.child_type or "").strip(),
    )
    profile_id = str(resolved.get("profile_id") or "").strip()
    family_name = str(resolved.get("family_id") or "").strip()
    child_type = str(resolved.get("child_type") or "").strip()
    if not child_type and profile_id and family_name:
        child_types = list_child_types(
            base_store_root=store_root,
            profile_id=profile_id,
            family_id=family_name,
        )
        if len(child_types) == 1:
            child_type = str(child_types[0] or "")
        elif len(child_types) > 1:
            payload = available_merge_child_types(
                store_root=store_root,
                profile_id=profile_id,
                family_id=family_name,
                child_types=child_types,
            )
            if bool(args.json):
                _print_json(payload)
                return
            print("Multiple staged child types found:")
            for idx, item in enumerate(list(payload.get("child_types") or []), start=1):
                print(f"{idx}. {item}")
            return
    if not profile_id or not family_name:
        payload = {
            "route": "canonical_merge",
            "profile_id": profile_id or None,
            "family_id": family_name or None,
            "child_type": child_type or None,
            "run_id": resolved.get("run_id"),
            "skills": [],
            "change_logs": [],
            "errors": [
                {
                    "stage": "canonical_merge",
                    "error": "could not resolve a unique staging bucket; pass --profile-id and --family-name explicitly",
                    "candidates": list(resolved.get("candidates") or []),
                }
            ],
        }
        if bool(args.json):
            _print_json(payload)
            return
        print("Canonical merge staging resolution failed.")
        _print_errors(list(payload.get("errors") or []))
        return
    payload = canonical_merge_from_staging(
        store_root=store_root,
        profile_id=profile_id,
        family_id=family_name,
        child_type=child_type,
        run_id=str(args.run_id or "").strip(),
    )
    if bool(args.json):
        _print_json(payload)
        return
    print("Canonical merge staging loaded.")
    print(
        f"profile={payload.get('profile_id') or ''} "
        f"family={payload.get('family_id') or ''} "
        f"child_type={payload.get('child_type') or ''} "
        f"run_id={payload.get('run_id') or ''}"
    )
    for idx, skill in enumerate(list(payload.get("skills") or [])[:20], start=1):
        print(f"{idx}. {skill.get('name', '')}")
    _print_errors(list(payload.get("errors") or []))


def _run_migrate_layout(args: argparse.Namespace) -> None:
    """Prepares `.runtime` layout under one document library root."""

    payload = migrate_layout(store_root=str(args.store_path or "").strip() or default_store_path())
    if bool(args.json):
        _print_json(payload)
        return
    print("Layout preparation completed.")
    print(f"store_root={payload.get('store_root', '')}")
    print(f"created={len(list(payload.get('created') or []))}")
    for path in list(payload.get("legacy_candidates") or []):
        print(f"legacy={path}")
    _print_errors(list(payload.get("errors") or []))


def main(argv: Optional[Sequence[str]] = None) -> None:
    """CLI entrypoint for staged document pipeline commands."""

    raw_args = list(argv if argv is not None else sys.argv[1:])
    parser = build_parser()
    if not raw_args:
        parser.print_help()
        return
    if raw_args[0].startswith("-") and raw_args[0] not in {"-h", "--help"}:
        raw_args = ["build"] + raw_args

    args = parser.parse_args(raw_args)
    command = str(args.command or "build").strip() or "build"
    if command in {"build", "llm-extract", "ingest", "extract", "compile", "diag"} and not str(args.file or "").strip():
        parser.error("--file is required for CLI commands. Use extract_from_doc(...) for in-memory data.")
    if command in {"build", "llm-extract"}:
        _run_build(args)
        return
    if command == "ingest":
        _run_ingest(args)
        return
    if command == "extract":
        _run_extract(args)
        return
    if command == "compile":
        _run_compile(args)
        return
    if command == "diag":
        _run_diag(args)
        return
    if command == "retrieve-hierarchy":
        _run_retrieve_hierarchy(args)
        return
    if command == "canonical-merge":
        _run_canonical_merge(args)
        return
    if command == "migrate-layout":
        _run_migrate_layout(args)
        return
    raise ValueError(f"unsupported command: {command}")


if __name__ == "__main__":
    main()
