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

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from autoskill import AutoSkill
from autoskill.config import default_document_store_path

from .common import StageLogger
from .compiler import (
    SkillCompilationResult,
    SkillCompiler,
    build_skill_compiler,
    compile_skills,
)
from .extractor import (
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
from .registry import DocumentRegistry, build_registry_from_store_config
from .versioning import VersionRegistrationResult, register_versions


@dataclass
class DocumentBuildResult:
    """Top-level result of a full offline document build run."""

    ingest: DocumentIngestResult
    extracted: SkillExtractionResult
    compiled: SkillCompilationResult
    registration: VersionRegistrationResult
    dry_run: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Returns a compact build summary suitable for CLI/API output."""

        return {
            "dry_run": bool(self.dry_run),
            "documents": len(self.ingest.documents),
            "skipped_documents": len(self.ingest.skipped_documents),
            "support_records": len(self.extracted.support_records),
            "skill_drafts": len(self.extracted.skill_drafts),
            "skill_specs": len(self.compiled.skill_specs),
            "lifecycles": len(self.registration.lifecycles),
            "change_logs": len(self.registration.change_logs),
            "version_history_entries": len(self.registration.version_history),
            "provenance_links": len(self.registration.provenance_links),
            "store_upserts": len(self.registration.upserted_store_skills),
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
            logger=self.logger,
        )

    def extract_skills(
        self,
        *,
        documents: List[DocumentRecord],
    ) -> SkillExtractionResult:
        """Runs the direct skill extraction stage only."""

        return extract_skills(
            documents=list(documents or []),
            extractor=self.document_skill_extractor,
            logger=self.logger,
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
        user_id: str,
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
            user_id=str(user_id or "").strip() or "u1",
            metadata=metadata,
            dry_run=dry_run,
            target_state=target_state,
            logger=self.logger,
        )

    def build(
        self,
        *,
        user_id: str,
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
    ) -> DocumentBuildResult:
        """Runs the full offline document build pipeline."""

        effective_state = target_state or (VersionState.DRAFT if dry_run else VersionState.ACTIVE)
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
        )
        extracted_result = self.extract_skills(documents=ingest_result.documents)
        compiled_result = self.compile_skills(
            skill_drafts=extracted_result.skill_drafts,
            support_records=extracted_result.support_records,
            target_state=effective_state,
        )
        registration_result = self.register_versions(
            documents=ingest_result.documents,
            support_records=compiled_result.support_records,
            skill_specs=compiled_result.skill_specs,
            user_id=user_id,
            metadata=metadata,
            dry_run=dry_run,
            target_state=effective_state,
        )
        return DocumentBuildResult(
            ingest=ingest_result,
            extracted=extracted_result,
            compiled=compiled_result,
            registration=registration_result,
            dry_run=bool(dry_run),
        )


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
        from .registry import default_registry_root

        registry = DocumentRegistry(root_dir=default_registry_root(default_document_store_path()))
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
