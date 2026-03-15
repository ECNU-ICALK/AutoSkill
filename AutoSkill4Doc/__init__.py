"""Offline document pipeline exports."""

from __future__ import annotations

from typing import Any

__all__ = [
    "extract_from_doc",
    "main",
    "default_store_path",
    "default_runtime_root",
    "default_registry_root",
    "DocumentBuildPipeline",
    "DocumentBuildResult",
    "build_default_document_pipeline",
    "ingest_document",
    "extract_skills",
    "compile_skills",
    "register_versions",
    "VersionManager",
    "sync_visible_skill_tree",
    "run_document_diag",
    "retrieve_hierarchy",
    "canonical_merge_from_staging",
    "migrate_layout",
    "DocumentRecord",
    "DocumentSection",
    "TextUnit",
    "StrictWindow",
    "SupportRecord",
    "SupportRelation",
    "SkillDraft",
    "SkillSpec",
    "SkillLifecycle",
    "VersionState",
    "TextSpan",
    "DocumentRegistry",
    "build_registry_from_store_config",
    "normalize_library_root",
    "runtime_root",
    "staging_root",
    "library_manifest_path",
    "latest_run_id",
    "list_child_types",
    "read_run_payload",
]


def __getattr__(name: str) -> Any:
    """Lazily resolves offline document pipeline exports."""

    if name == "extract_from_doc":
        from .extract import extract_from_doc as fn

        return fn
    if name == "main":
        from .extract import main as fn

        return fn
    if name in {"default_store_path", "default_runtime_root", "default_registry_root"}:
        from .core.config import default_registry_root, default_runtime_root, default_store_path

        mapping = {
            "default_store_path": default_store_path,
            "default_runtime_root": default_runtime_root,
            "default_registry_root": default_registry_root,
        }
        return mapping[name]
    if name in {
        "DocumentBuildPipeline",
        "DocumentBuildResult",
        "build_default_document_pipeline",
    }:
        from .pipeline import (
            DocumentBuildPipeline,
            DocumentBuildResult,
            build_default_document_pipeline,
        )

        mapping = {
            "DocumentBuildPipeline": DocumentBuildPipeline,
            "DocumentBuildResult": DocumentBuildResult,
            "build_default_document_pipeline": build_default_document_pipeline,
        }
        return mapping[name]
    if name in {
        "ingest_document",
        "extract_skills",
        "compile_skills",
        "register_versions",
        "VersionManager",
        "sync_visible_skill_tree",
        "run_document_diag",
        "retrieve_hierarchy",
        "canonical_merge_from_staging",
        "migrate_layout",
    }:
        from .ingest import ingest_document
        from .stages.compiler import compile_skills
        from .stages.diag import run_document_diag
        from .stages.extractor import extract_skills
        from .stages.hierarchy import retrieve_hierarchy
        from .stages.merge import canonical_merge_from_staging
        from .stages.migrate import migrate_layout
        from .store.versioning import VersionManager, register_versions
        from .store.visible_tree import sync_visible_skill_tree

        mapping = {
            "ingest_document": ingest_document,
            "extract_skills": extract_skills,
            "compile_skills": compile_skills,
            "register_versions": register_versions,
            "VersionManager": VersionManager,
            "sync_visible_skill_tree": sync_visible_skill_tree,
            "run_document_diag": run_document_diag,
            "retrieve_hierarchy": retrieve_hierarchy,
            "canonical_merge_from_staging": canonical_merge_from_staging,
            "migrate_layout": migrate_layout,
        }
        return mapping[name]
    if name in {
        "DocumentRecord",
        "DocumentSection",
        "TextUnit",
        "StrictWindow",
        "SupportRecord",
        "SupportRelation",
        "SkillDraft",
        "SkillSpec",
        "SkillLifecycle",
        "VersionState",
        "TextSpan",
    }:
        from .models import (
            DocumentRecord,
            DocumentSection,
            StrictWindow,
            SkillDraft,
            SkillLifecycle,
            SkillSpec,
            SupportRecord,
            SupportRelation,
            TextUnit,
            TextSpan,
            VersionState,
        )

        mapping = {
            "DocumentRecord": DocumentRecord,
            "DocumentSection": DocumentSection,
            "TextUnit": TextUnit,
            "StrictWindow": StrictWindow,
            "SupportRecord": SupportRecord,
            "SupportRelation": SupportRelation,
            "SkillDraft": SkillDraft,
            "SkillSpec": SkillSpec,
            "SkillLifecycle": SkillLifecycle,
            "VersionState": VersionState,
            "TextSpan": TextSpan,
        }
        return mapping[name]
    if name in {
        "DocumentRegistry",
        "build_registry_from_store_config",
        "normalize_library_root",
        "runtime_root",
        "staging_root",
        "library_manifest_path",
        "latest_run_id",
        "list_child_types",
        "read_run_payload",
    }:
        from .store.registry import (
            DocumentRegistry,
            build_registry_from_store_config,
        )
        from .store.layout import library_manifest_path, normalize_library_root, runtime_root, staging_root
        from .store.staging import latest_run_id, list_child_types, read_run_payload

        mapping = {
            "DocumentRegistry": DocumentRegistry,
            "build_registry_from_store_config": build_registry_from_store_config,
            "normalize_library_root": normalize_library_root,
            "runtime_root": runtime_root,
            "staging_root": staging_root,
            "library_manifest_path": library_manifest_path,
            "latest_run_id": latest_run_id,
            "list_child_types": list_child_types,
            "read_run_payload": read_run_payload,
        }
        return mapping[name]
    raise AttributeError(name)
