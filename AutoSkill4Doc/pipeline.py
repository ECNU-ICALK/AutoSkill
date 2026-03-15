"""
Staged offline document pipeline orchestration.

The pipeline is organized as explicit stages so callers can rerun or override
any stage independently:
- ingest_document
- extract_skills
- compile_skills
- register_versions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from autoskill import AutoSkill

from .core.common import StageLogger
from .core.config import DEFAULT_DOC_SKILL_USER_ID, DEFAULT_EXTRACT_STRATEGY, default_store_path
from .stages.compiler import (
    SkillCompilationResult,
    SkillCompiler,
    build_skill_compiler,
    compile_skills,
)
from .stages.extractor import (
    DocumentSkillExtractor,
    SkillExtractionResult,
    build_document_skill_extractor,
    extract_skills,
)
from .ingest import (
    DocumentIngestResult,
    DocumentIngestor,
    HeuristicDocumentIngestor,
    ingest_document,
)
from .models import DocumentRecord, SkillDraft, SkillSpec, SupportRecord, VersionState
from .models import StrictWindow
from .store.intermediate import IntermediateRunWriter, new_intermediate_run_id
from .store.registry import DocumentRegistry, build_registry_from_store_config
from .store.versioning import VersionRegistrationResult, register_versions


@dataclass
class DocumentBuildResult:
    """Top-level result of a full offline document build run."""

    ingest: DocumentIngestResult
    extracted: SkillExtractionResult
    compiled: SkillCompilationResult
    registration: VersionRegistrationResult
    dry_run: bool = False
    intermediate: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Returns a compact build summary suitable for CLI/API output."""

        return {
            "dry_run": bool(self.dry_run),
            "documents": len(self.ingest.documents),
            "skipped_documents": len(self.ingest.skipped_documents),
            "windows": len(self.ingest.windows),
            "support_records": len(self.compiled.support_records),
            "skill_drafts": len(self.extracted.skill_drafts),
            "skill_specs": len(self.compiled.skill_specs),
            "lifecycles": len(self.registration.lifecycles),
            "change_logs": len(self.registration.change_logs),
            "version_history_entries": len(self.registration.version_history),
            "provenance_links": len(self.registration.provenance_links),
            "store_upserts": len(self.registration.upserted_store_skills),
            "staging_runs": len(self.registration.staging_runs),
            "visible_families": len(list((self.registration.visible_tree or {}).get("affected_families") or [])),
            "visible_children": len(list((self.registration.visible_tree or {}).get("child_paths") or [])),
            "intermediate": dict(self.intermediate or {}),
            "errors": (
                list(self.ingest.errors)
                + list(self.extracted.errors)
                + list(self.compiled.errors)
                + list(self.registration.errors)
            ),
        }


class DocumentBuildPipeline:
    """Composable staged pipeline for offline document compilation."""

    def __init__(
        self,
        *,
        registry: DocumentRegistry,
        sdk: Optional[AutoSkill] = None,
        document_ingestor: Optional[DocumentIngestor] = None,
        document_skill_extractor: Optional[DocumentSkillExtractor] = None,
        skill_compiler: Optional[SkillCompiler] = None,
        logger: StageLogger = None,
    ) -> None:
        """Builds a pipeline with replaceable stage implementations."""

        self.registry = registry
        self.sdk = sdk
        self.document_ingestor = document_ingestor or HeuristicDocumentIngestor()
        self.document_skill_extractor = document_skill_extractor or build_document_skill_extractor("llm")
        self.skill_compiler = skill_compiler or build_skill_compiler("llm")
        self.logger = logger

    def ingest_document(
        self,
        *,
        data: Optional[Any] = None,
        file_path: str = "",
        title: str = "",
        source_type: str = "document",
        domain: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        continue_on_error: bool = True,
        dry_run: bool = False,
        max_documents: int = 0,
        extract_strategy: str = DEFAULT_EXTRACT_STRATEGY,
    ) -> DocumentIngestResult:
        """Runs the ingestion stage only."""

        return ingest_document(
            data=data,
            file_path=file_path,
            title=title,
            source_type=source_type,
            domain=domain,
            metadata=metadata,
            registry=self.registry,
            ingestor=self.document_ingestor,
            continue_on_error=continue_on_error,
            dry_run=dry_run,
            max_documents=max_documents,
            extract_strategy=extract_strategy,
            logger=self.logger,
        )

    def extract_skills(
        self,
        *,
        documents: List[DocumentRecord],
        windows: Optional[List[StrictWindow]] = None,
        progress_callback=None,
        accumulate_result: bool = True,
    ) -> SkillExtractionResult:
        """Runs the direct skill extraction stage only."""

        return extract_skills(
            documents=list(documents or []),
            windows=list(windows or []),
            extractor=self.document_skill_extractor,
            logger=self.logger,
            progress_callback=progress_callback,
            accumulate_result=accumulate_result,
        )

    def compile_skills(
        self,
        *,
        skill_drafts: List[SkillDraft],
        support_records: List[SupportRecord],
        target_state: VersionState = VersionState.DRAFT,
    ) -> SkillCompilationResult:
        """Runs the skill compilation stage only."""

        return compile_skills(
            skill_drafts=list(skill_drafts or []),
            support_records=list(support_records or []),
            compiler=self.skill_compiler,
            target_state=target_state,
            logger=self.logger,
        )

    def register_versions(
        self,
        *,
        documents: List[DocumentRecord],
        support_records: List[SupportRecord],
        skill_specs: List[SkillSpec],
        user_id: str = DEFAULT_DOC_SKILL_USER_ID,
        metadata: Optional[Dict[str, Any]] = None,
        dry_run: bool = False,
        target_state: VersionState = VersionState.ACTIVE,
    ) -> VersionRegistrationResult:
        """Runs the registry/version registration stage only."""

        return register_versions(
            registry=self.registry,
            documents=list(documents or []),
            support_records=list(support_records or []),
            skill_specs=list(skill_specs or []),
            sdk=self.sdk,
            user_id=str(user_id or "").strip() or DEFAULT_DOC_SKILL_USER_ID,
            metadata=metadata,
            dry_run=dry_run,
            target_state=target_state,
            logger=self.logger,
        )

    def build(
        self,
        *,
        user_id: str = DEFAULT_DOC_SKILL_USER_ID,
        data: Optional[Any] = None,
        file_path: str = "",
        title: str = "",
        source_type: str = "document",
        domain: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        continue_on_error: bool = True,
        dry_run: bool = False,
        target_state: Optional[VersionState] = None,
        max_documents: int = 0,
        extract_strategy: str = DEFAULT_EXTRACT_STRATEGY,
    ) -> DocumentBuildResult:
        """Runs the full offline document build pipeline."""

        effective_state = target_state or (VersionState.DRAFT if dry_run else VersionState.ACTIVE)
        intermediate_writer = None
        intermediate_summary: Dict[str, Any] = {}
        if not dry_run:
            store_root = ""
            if self.sdk is not None:
                store_root = str(getattr(getattr(self.sdk, "config", None), "store", {}).get("path") or "").strip()
            if not store_root:
                registry_root = os.path.abspath(os.path.expanduser(str(self.registry.root_dir or "").strip()))
                runtime_dir = os.path.dirname(registry_root)
                if os.path.basename(runtime_dir) == ".runtime":
                    store_root = os.path.dirname(runtime_dir)
            if store_root:
                intermediate_writer = IntermediateRunWriter(
                    base_store_root=store_root,
                    run_id=new_intermediate_run_id(),
                    metadata=metadata,
                )
                intermediate_summary = intermediate_writer.summary().to_dict()
        ingest_result = self.ingest_document(
            data=data,
            file_path=file_path,
            title=title,
            source_type=source_type,
            domain=domain,
            metadata=metadata,
            continue_on_error=continue_on_error,
            dry_run=dry_run,
            max_documents=max_documents,
            extract_strategy=extract_strategy,
        )
        if intermediate_writer is not None:
            intermediate_writer.write_ingest(ingest_result)
            intermediate_summary = intermediate_writer.summary().to_dict()
        try:
            extracted_result = self.extract_skills(
                documents=ingest_result.documents,
                windows=ingest_result.windows,
                accumulate_result=(intermediate_writer is None),
                progress_callback=(
                    None
                    if intermediate_writer is None
                    else lambda record, supports, drafts, cumulative: intermediate_writer.write_extract_progress(
                        record=record,
                        supports=supports,
                        drafts=drafts,
                        total_documents=len(ingest_result.documents),
                    )
                ),
            )
            if intermediate_writer is not None:
                extracted_result = intermediate_writer.load_extract()
                intermediate_writer.write_extract(extracted_result)
                intermediate_summary = intermediate_writer.summary().to_dict()
            compiled_result = self.compile_skills(
                skill_drafts=extracted_result.skill_drafts,
                support_records=extracted_result.support_records,
                target_state=effective_state,
            )
            if intermediate_writer is not None:
                intermediate_writer.write_compile(compiled_result)
                intermediate_summary = intermediate_writer.summary().to_dict()
            registration_result = self.register_versions(
                documents=ingest_result.documents,
                support_records=compiled_result.support_records,
                skill_specs=compiled_result.skill_specs,
                user_id=user_id,
                metadata=metadata,
                dry_run=dry_run,
                target_state=effective_state,
            )
            if intermediate_writer is not None:
                intermediate_writer.write_registration(registration_result)
                intermediate_summary = intermediate_writer.summary().to_dict()
            build_result = DocumentBuildResult(
                ingest=ingest_result,
                extracted=extracted_result,
                compiled=compiled_result,
                registration=registration_result,
                dry_run=bool(dry_run),
                intermediate=dict(intermediate_summary or {}),
            )
            if intermediate_writer is not None:
                intermediate_writer.complete(summary=build_result.to_dict())
                intermediate_summary = intermediate_writer.summary().to_dict()
                build_result.intermediate = dict(intermediate_summary or {})
            return build_result
        except Exception as exc:
            if intermediate_writer is not None:
                intermediate_writer.fail(error=str(exc))
            raise


def build_default_document_pipeline(
    *,
    sdk: Optional[AutoSkill] = None,
    registry_root: str = "",
    logger: StageLogger = None,
    document_skill_extractor: Optional[DocumentSkillExtractor] = None,
    skill_compiler: Optional[SkillCompiler] = None,
) -> DocumentBuildPipeline:
    """Builds the default staged document pipeline."""

    if registry_root:
        registry = DocumentRegistry(root_dir=registry_root)
    elif sdk is not None:
        registry = build_registry_from_store_config(dict(getattr(getattr(sdk, "config", None), "store", {}) or {}))
    else:
        from .store.registry import default_registry_root

        registry = DocumentRegistry(root_dir=default_registry_root(default_store_path()))
    return DocumentBuildPipeline(
        registry=registry,
        sdk=sdk,
        logger=logger,
        document_skill_extractor=document_skill_extractor
        or build_document_skill_extractor(
            "llm",
            llm_config=dict(getattr(getattr(sdk, "config", None), "llm", {}) or {}),
        ),
        skill_compiler=skill_compiler
        or build_skill_compiler(
            "llm",
            llm_config=dict(getattr(getattr(sdk, "config", None), "llm", {}) or {}),
        ),
    )
