"""
Staged offline document pipeline entrypoints.

This module wires the skill-first document pipeline into the existing AutoSkill
SDK style:
- `extract_from_doc(...)` remains the programmatic entrypoint
- `main()` exposes a small CLI with stage-oriented commands

Commands:
- `build`: full document -> skill draft -> canonical skill -> registry/store flow
- `ingest`: only normalize/import documents and run incremental checks
- `extract`: stop after support record and skill draft extraction
- `compile`: stop after canonical skill compilation without persisting registry/store updates
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.config import default_document_store_path

from .common import StageLogger
from .extractor import build_document_skill_extractor
from .models import DocumentRecord, SkillDraft, SkillSpec, SupportRecord, VersionState
from .pipeline import DocumentBuildPipeline, DocumentBuildResult, build_default_document_pipeline
from ..provider_config import (
    build_embeddings_config as _build_provider_embeddings_config,
    build_llm_config as _build_provider_llm_config,
)

_DOCUMENT_CLI_EXAMPLES = (
    "Examples:\n"
    "  autoskill offline document build --file ./paper.md --dry-run\n"
    "  autoskill offline document extract --file ./docs/ --json\n"
    "  autoskill offline document compile --file ./manual.md --json"
)


def extract_from_doc(
    *,
    sdk: AutoSkill,
    user_id: str,
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
    domain_profile_path: str = "",
    dry_run: bool = False,
    target_state: Optional[VersionState] = None,
    logger: StageLogger = None,
    max_documents: int = 0,
    max_candidates_per_unit: int = 3,
    max_units_per_document: int = 0,
) -> Dict[str, Any]:
    """
    Runs the staged offline document pipeline and returns a compact summary.
    """

    md = dict(metadata or {})
    md.setdefault("channel", "offline_extract_from_doc")
    md.setdefault("source_type", str(source_type or "").strip() or "document")
    if hint and str(hint).strip():
        md.setdefault("hint", str(hint).strip())

    pipeline = build_default_document_pipeline(
        sdk=sdk,
        registry_root=str(registry_root or "").strip(),
        logger=logger,
        document_skill_extractor=build_document_skill_extractor(
            "llm",
            llm_config=dict(getattr(getattr(sdk, "config", None), "llm", {}) or {}),
            max_section_chars=int(max_chars_per_chunk or 0) or 6000,
            overlap_chars=int(overlap_chars or 0),
            domain_profile_path=str(domain_profile_path or "").strip(),
            max_candidates_per_unit=int(max_candidates_per_unit or 0) or 3,
            max_units_per_document=int(max_units_per_document or 0),
        ),
    )
    result = pipeline.build(
        user_id=str(user_id or "").strip() or "u1",
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
        "total_support_records": len(result.extracted.support_records),
        "total_skill_drafts": len(result.extracted.skill_drafts),
        "total_skill_specs": len(result.compiled.skill_specs),
        "lifecycle_events": len(result.registration.lifecycles),
        "change_events": len(result.registration.change_logs),
        "version_history_entries": len(result.registration.version_history),
        "provenance_links": len(result.registration.provenance_links),
        "upserted_count": len(result.registration.upserted_store_skills),
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
        "path": str(args.store_path or "").strip() or default_document_store_path(),
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
    return build_default_document_pipeline(
        sdk=sdk,
        registry_root=str(args.registry_root or "").strip(),
        logger=(None if bool(args.quiet) else print),
        document_skill_extractor=build_document_skill_extractor(
            "llm",
            llm_config=dict(getattr(getattr(sdk, "config", None), "llm", {}) or {}),
            max_section_chars=int(args.max_chars_per_chunk or 0) or 6000,
            overlap_chars=int(args.overlap_chars or 0),
            domain_profile_path=str(args.domain_profile or "").strip(),
            max_candidates_per_unit=int(args.max_candidates_per_unit or 0) or 3,
            max_units_per_document=int(args.max_units_per_document or 0),
        ),
    )


def _base_metadata(args: argparse.Namespace) -> Dict[str, Any]:
    """Builds common metadata shared across CLI commands."""

    md = {"channel": "offline_extract_from_doc", "source_type": str(args.source_type or "").strip() or "document"}
    if str(args.hint or "").strip():
        md["hint"] = str(args.hint).strip()
    return md


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Adds shared document CLI arguments."""

    parser.add_argument("--file", default="", help="Single file or directory containing offline documents.")
    parser.add_argument("--title", default="", help="Optional document title override for inline input.")
    parser.add_argument("--domain", default="", help="Optional domain hint, e.g. psychology or chemistry.")
    parser.add_argument("--source-type", default="document", help="Generic source type label stored with imported documents.")
    parser.add_argument(
        "--registry-root",
        default="",
        help="Override the document registry root. Default: <store>/.autoskill/document_registry.",
    )
    parser.add_argument(
        "--store-path",
        default="",
        help="AutoSkill local store path. Default: <repo_root>/SkillBank/DocSkill.",
    )
    parser.add_argument("--user-id", default="u1", help="Target user id for resulting skill maintenance.")
    parser.add_argument("--hint", default="", help="Optional extraction hint stored in metadata.")
    parser.add_argument(
        "--domain-profile",
        default="",
        help="Optional JSON file overriding or extending the built-in domain profile used by the document extractor.",
    )
    parser.add_argument("--continue-on-error", action="store_true", help="Continue processing documents after extraction errors.")
    parser.add_argument("--dry-run", action="store_true", help="Run extraction/versioning without persisting registry or store changes.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    parser.add_argument("--quiet", action="store_true", help="Suppress stage logs and only print final output.")
    parser.add_argument("--max-documents", type=int, default=0, help="Limit how many files are read when --file points to a directory. 0 means no limit.")

    parser.add_argument("--llm-provider", default="mock", help="LLM provider id used by AutoSkill.")
    parser.add_argument("--llm-model", default="", help="LLM model id.")
    parser.add_argument("--llm-base-url", default="", help="Optional LLM base URL.")
    parser.add_argument("--llm-api-key", default=os.getenv("OPENAI_API_KEY", ""), help=argparse.SUPPRESS)
    parser.add_argument("--auth-mode", default="", help=argparse.SUPPRESS)
    parser.add_argument("--llm-response", default="", help=argparse.SUPPRESS)

    parser.add_argument("--embeddings-provider", default="", help="Embeddings provider id.")
    parser.add_argument("--embeddings-model", default="", help="Embeddings model id.")
    parser.add_argument("--embeddings-base-url", default="", help="Optional embeddings base URL.")
    parser.add_argument("--embeddings-api-key", default=os.getenv("OPENAI_API_KEY", ""), help=argparse.SUPPRESS)
    parser.add_argument("--embeddings-auth-mode", default="", help=argparse.SUPPRESS)
    parser.add_argument("--embeddings-dims", type=int, default=64, help="Embedding dimensions for hashing/mock providers.")
    parser.add_argument("--maintenance-strategy", default="llm", choices=["heuristic", "llm"], help="Store maintenance strategy.")

    parser.add_argument(
        "--max-chars-per-chunk",
        type=int,
        default=6000,
        help="Maximum characters per extraction unit. Short sections stay whole; long sections fall back to smaller chunks.",
    )
    parser.add_argument(
        "--overlap-chars",
        type=int,
        default=300,
        help="Overlap used when a long section must be split into fallback chunks.",
    )
    parser.add_argument(
        "--max-candidates-per-unit",
        type=int,
        default=3,
        help="Maximum skill candidates requested from the model for each extraction unit.",
    )
    parser.add_argument(
        "--max-units-per-document",
        type=int,
        default=0,
        help="Limit how many section/chunk units are sent to the model per document. 0 means no limit.",
    )


def build_parser() -> argparse.ArgumentParser:
    """Builds the document pipeline CLI parser."""

    parser = argparse.ArgumentParser(
        description="Run the skill-first offline AutoSkill document pipeline.",
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
        user_id=str(args.user_id or "").strip() or "u1",
        file_path=str(args.file or "").strip(),
        title=str(args.title or "").strip(),
        source_type=str(args.source_type or "").strip() or "document",
        domain=str(args.domain or "").strip(),
        metadata=_base_metadata(args),
        continue_on_error=bool(args.continue_on_error),
        dry_run=bool(args.dry_run),
        target_state=_coerce_state(str(args.target_state or ""), default=VersionState.ACTIVE),
        max_documents=int(args.max_documents or 0),
    )
    payload = _build_summary(pipeline=pipeline, result=result)
    if bool(args.json):
        _print_json(payload)
        return
    print("Offline document build completed.")
    print(
        f"documents={payload['total_documents']} "
        f"skipped={payload['skipped_documents']} "
        f"supports={payload['total_support_records']} "
        f"drafts={payload['total_skill_drafts']} "
        f"skills={payload['total_skill_specs']} "
        f"changes={payload['change_events']}"
    )
    for idx, skill in enumerate(list(payload.get("skills") or [])[:20], start=1):
        print(f"{idx}. {skill.get('name', '')} ({skill.get('version', '')}, {skill.get('status', '')})")
    _print_errors(list(payload.get("errors") or []))


def _run_ingest(args: argparse.Namespace) -> None:
    """Runs only the ingestion stage."""

    pipeline = _build_pipeline_from_args(args)
    result = pipeline.ingest_document(
        file_path=str(args.file or "").strip(),
        title=str(args.title or "").strip(),
        source_type=str(args.source_type or "").strip() or "document",
        domain=str(args.domain or "").strip(),
        metadata=_base_metadata(args),
        continue_on_error=bool(args.continue_on_error),
        dry_run=bool(args.dry_run),
        max_documents=int(args.max_documents or 0),
    )
    payload = {
        "documents": [_plain_document(doc) for doc in list(result.documents or [])],
        "skipped_documents": [_plain_document(doc) for doc in list(result.skipped_documents or [])],
        "errors": list(result.errors or []),
    }
    if bool(args.json):
        _print_json(payload)
        return
    print("Offline document ingest completed.")
    print(f"documents={len(result.documents)} skipped={len(result.skipped_documents)}")
    _print_errors(list(result.errors or []))


def _run_extract(args: argparse.Namespace) -> None:
    """Runs through direct skill extraction only."""

    pipeline = _build_pipeline_from_args(args)
    ingest_result = pipeline.ingest_document(
        file_path=str(args.file or "").strip(),
        title=str(args.title or "").strip(),
        source_type=str(args.source_type or "").strip() or "document",
        domain=str(args.domain or "").strip(),
        metadata=_base_metadata(args),
        continue_on_error=bool(args.continue_on_error),
        dry_run=bool(args.dry_run),
        max_documents=int(args.max_documents or 0),
    )
    extracted_result = pipeline.extract_skills(documents=ingest_result.documents)
    payload = {
        "documents": [_plain_document(doc) for doc in list(ingest_result.documents or [])],
        "skipped_documents": [_plain_document(doc) for doc in list(ingest_result.skipped_documents or [])],
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
        f"supports={len(extracted_result.support_records)} "
        f"drafts={len(extracted_result.skill_drafts)}"
    )
    _print_errors(list(payload.get("errors") or []))


def _run_compile(args: argparse.Namespace) -> None:
    """Runs through canonical skill compilation without registry writes."""

    pipeline = _build_pipeline_from_args(args)
    ingest_result = pipeline.ingest_document(
        file_path=str(args.file or "").strip(),
        title=str(args.title or "").strip(),
        source_type=str(args.source_type or "").strip() or "document",
        domain=str(args.domain or "").strip(),
        metadata=_base_metadata(args),
        continue_on_error=bool(args.continue_on_error),
        dry_run=True,
        max_documents=int(args.max_documents or 0),
    )
    extracted_result = pipeline.extract_skills(documents=ingest_result.documents)
    compiled_result = pipeline.compile_skills(
        skill_drafts=extracted_result.skill_drafts,
        support_records=extracted_result.support_records,
        target_state=_coerce_state(str(args.target_state or ""), default=VersionState.DRAFT),
    )
    payload = {
        "documents": [_plain_document(doc) for doc in list(ingest_result.documents or [])],
        "skipped_documents": [_plain_document(doc) for doc in list(ingest_result.skipped_documents or [])],
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
        f"supports={len(compiled_result.support_records)} "
        f"drafts={len(compiled_result.skill_drafts)} "
        f"skills={len(compiled_result.skill_specs)}"
    )
    for idx, spec in enumerate(list(compiled_result.skill_specs or [])[:20], start=1):
        print(f"{idx}. {spec.name} ({spec.version}, {spec.status.value})")
    _print_errors(list(payload.get("errors") or []))


def main(argv: Optional[Sequence[str]] = None) -> None:
    """CLI entrypoint for staged document pipeline commands."""

    raw_args = list(argv if argv is not None else sys.argv[1:])
    if not raw_args:
        build_parser().print_help()
        return
    if raw_args[0].startswith("-") and raw_args[0] not in {"-h", "--help"}:
        raw_args = ["build"] + raw_args

    args = build_parser().parse_args(raw_args)
    command = str(args.command or "build").strip() or "build"
    if command == "build":
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
    raise ValueError(f"unsupported command: {command}")


if __name__ == "__main__":
    main()
