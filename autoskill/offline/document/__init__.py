"""Offline document pipeline exports."""

from __future__ import annotations

from typing import Any

__all__ = [
    "extract_from_doc",
    "main",
    "DocumentBuildPipeline",
    "DocumentBuildResult",
    "build_default_document_pipeline",
    "ingest_document",
    "extract_skills",
    "compile_skills",
    "register_versions",
    "VersionManager",
    "DocumentRecord",
    "DocumentSection",
    "SupportRecord",
    "SupportRelation",
    "SkillDraft",
    "SkillSpec",
    "SkillLifecycle",
    "VersionState",
    "TextSpan",
    "DomainProfile",
    "KeywordGroup",
    "load_domain_profile",
    "list_builtin_domain_profiles",
    "DocumentRegistry",
    "build_registry_from_store_config",
    "default_registry_root",
]


def __getattr__(name: str) -> Any:
    """Lazily resolves offline document pipeline exports."""

    if name == "extract_from_doc":
        from .extract import extract_from_doc as fn

        return fn
    if name == "main":
        from .extract import main as fn

        return fn
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
    }:
        from .compiler import compile_skills
        from .extractor import extract_skills
        from .ingest import ingest_document
        from .versioning import VersionManager, register_versions

        mapping = {
            "ingest_document": ingest_document,
            "extract_skills": extract_skills,
            "compile_skills": compile_skills,
            "register_versions": register_versions,
            "VersionManager": VersionManager,
        }
        return mapping[name]
    if name in {
        "DocumentRecord",
        "DocumentSection",
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
            SkillDraft,
            SkillLifecycle,
            SkillSpec,
            SupportRecord,
            SupportRelation,
            TextSpan,
            VersionState,
        )

        mapping = {
            "DocumentRecord": DocumentRecord,
            "DocumentSection": DocumentSection,
            "SupportRecord": SupportRecord,
            "SupportRelation": SupportRelation,
            "SkillDraft": SkillDraft,
            "SkillSpec": SkillSpec,
            "SkillLifecycle": SkillLifecycle,
            "VersionState": VersionState,
            "TextSpan": TextSpan,
        }
        return mapping[name]
    if name in {"DomainProfile", "KeywordGroup", "load_domain_profile", "list_builtin_domain_profiles"}:
        from .profile import DomainProfile, KeywordGroup, list_builtin_domain_profiles, load_domain_profile

        mapping = {
            "DomainProfile": DomainProfile,
            "KeywordGroup": KeywordGroup,
            "load_domain_profile": load_domain_profile,
            "list_builtin_domain_profiles": list_builtin_domain_profiles,
        }
        return mapping[name]
    if name in {"DocumentRegistry", "build_registry_from_store_config", "default_registry_root"}:
        from .registry import (
            DocumentRegistry,
            build_registry_from_store_config,
            default_registry_root,
        )

        mapping = {
            "DocumentRegistry": DocumentRegistry,
            "build_registry_from_store_config": build_registry_from_store_config,
            "default_registry_root": default_registry_root,
        }
        return mapping[name]
    raise AttributeError(name)
