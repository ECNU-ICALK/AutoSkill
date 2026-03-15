"""Registry and versioning helpers for AutoSkill4Doc."""

from .intermediate import IntermediateRunSummary, IntermediateRunWriter, new_intermediate_run_id
from .layout import (
    intermediate_run_dir,
    intermediate_runs_root,
    library_manifest_path,
    normalize_library_root,
    registry_root,
    runtime_root,
    staging_root,
)
from .retrieval import (
    DEFAULT_RETRIEVAL_LIMIT,
    DocumentSkillRetriever,
    SkillRetrievalHit,
    build_document_skill_retriever,
    skill_retrieval_text,
)
from .registry import DocumentRegistry, build_registry_from_store_config, default_registry_root
from .staging import (
    discover_staging_buckets,
    latest_run_id,
    list_child_types,
    read_run_payload,
    resolve_staging_bucket_context,
    write_registration_staging,
)
from .visible_tree import VisibleTreeSyncResult, sync_visible_skill_tree
from .versioning import VersionManager, register_versions

__all__ = [
    "normalize_library_root",
    "runtime_root",
    "registry_root",
    "staging_root",
    "intermediate_runs_root",
    "intermediate_run_dir",
    "library_manifest_path",
    "SkillRetrievalHit",
    "DocumentSkillRetriever",
    "build_document_skill_retriever",
    "skill_retrieval_text",
    "DEFAULT_RETRIEVAL_LIMIT",
    "IntermediateRunSummary",
    "IntermediateRunWriter",
    "new_intermediate_run_id",
    "DocumentRegistry",
    "build_registry_from_store_config",
    "default_registry_root",
    "discover_staging_buckets",
    "write_registration_staging",
    "read_run_payload",
    "latest_run_id",
    "list_child_types",
    "resolve_staging_bucket_context",
    "VisibleTreeSyncResult",
    "sync_visible_skill_tree",
    "VersionManager",
    "register_versions",
]
