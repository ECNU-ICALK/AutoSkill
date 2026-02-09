"""
SDK entrypoint: AutoSkill.

Responsibilities:
1) ingest: accept conversations/events -> extract candidate Skills
2) maintain: dedupe/merge/bump version, and generate/update Agent Skill artifacts (SKILL.md)
3) search: vector-search relevant Skills for the current task
4) export/write: export as `anthropics/skills`-style “skill directory artifacts”
"""

from __future__ import annotations

import inspect
import uuid
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional

from .config import AutoSkillConfig
from .skill_management.formats.agent_skill import build_agent_skill_files
from .models import Skill, SkillHit
from .render import render_skills_context
from .skill_management.extraction import SkillExtractor, build_default_extractor
from .skill_management.maintenance import SkillMaintainer
from .skill_management.artifacts import (
    export_skill_dir as _export_skill_dir,
    export_skill_md as _export_skill_md,
    write_skill_dir as _write_skill_dir,
    write_skill_dirs as _write_skill_dirs,
)
from .skill_management.importer import import_agent_skill_dirs as _import_agent_skill_dirs
from .skill_management.stores.base import SkillStore
from .skill_management.stores.factory import build_store
from .utils.time import now_iso


class AutoSkill:
    """
    SDK entrypoint.

    Responsibilities:
    - Ingest conversation/events
    - Extract candidate skills
    - Maintain skill set (dedupe/merge/version)
    - Retrieve skills for downstream tasks
    """

    def __init__(
        self,
        config: Optional[AutoSkillConfig] = None,
        *,
        store: Optional[SkillStore] = None,
        extractor: Optional[SkillExtractor] = None,
    ) -> None:
        """
        Builds an SDK instance with pluggable store and extractor implementations.

        Defaults:
        - store: built from `config.store`
        - extractor: built from `config.llm`
        """

        self.config = config or AutoSkillConfig()
        self.store = store or build_store(self.config)
        self.extractor = extractor or build_default_extractor(self.config)
        self.maintainer = SkillMaintainer(self.config, self.store, self.extractor)

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "AutoSkill":
        """Constructs `AutoSkill` from a plain dict config."""

        return cls(AutoSkillConfig.from_dict(config))

    def ingest(
        self,
        *,
        messages: Optional[List[Dict[str, Any]]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ) -> List[Skill]:
        """
        End-to-end learning entrypoint.

        Flow:
        1) extract candidate skills from messages/events
        2) maintain skill set (add/merge/discard + versioning)
        3) persist via configured store
        """

        if not messages and not events:
            raise ValueError("ingest requires either messages or events")

        md = dict(metadata or {})
        # Extraction consumes only caller-provided retrieval reference (top1 or None).
        # SDK does not run a second retrieval to avoid duplicate/lagging behavior.
        raw_ref = md.get("extraction_reference")
        retrieved_reference = dict(raw_ref) if isinstance(raw_ref, dict) else None

        # 1) Extract candidates (LLM or heuristic)
        # Extract at most one Skill per ingest to keep quality high and avoid noisy skill spam.
        max_candidates = max(0, min(1, int(self.config.max_candidates_per_ingest)))
        extracted = self._extract_candidates(
            user_id=user_id,
            messages=messages,
            events=events,
            max_candidates=max_candidates,
            hint=hint,
            retrieved_reference=retrieved_reference,
        )
        # 2) Maintain (dedupe/merge/version) and persist to store
        return self.maintainer.apply(extracted, user_id=user_id, metadata=metadata)

    def extract_candidates(
        self,
        *,
        user_id: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        hint: Optional[str] = None,
        max_candidates: Optional[int] = None,
        retrieved_reference: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Extracts candidate skills without persisting (for simulation/debug APIs).
        """

        if not messages and not events:
            raise ValueError("extract_candidates requires either messages or events")
        limit = (
            max(0, int(max_candidates))
            if max_candidates is not None
            else max(0, min(1, int(self.config.max_candidates_per_ingest)))
        )
        return self._extract_candidates(
            user_id=user_id,
            messages=messages,
            events=events,
            max_candidates=limit,
            hint=hint,
            retrieved_reference=(
                dict(retrieved_reference) if isinstance(retrieved_reference, dict) else None
            ),
        )

    def _extract_candidates(
        self,
        *,
        user_id: str,
        messages: Optional[List[Dict[str, Any]]],
        events: Optional[List[Dict[str, Any]]],
        max_candidates: int,
        hint: Optional[str],
        retrieved_reference: Optional[Dict[str, Any]],
    ) -> List[Any]:
        """
        Calls extractor with backward compatibility for custom extractors that do not yet
        accept `retrieved_reference`.
        """

        fn = self.extractor.extract
        supports_reference = False
        try:
            supports_reference = "retrieved_reference" in inspect.signature(fn).parameters
        except Exception:
            supports_reference = False

        if supports_reference:
            return fn(
                user_id=user_id,
                messages=messages,
                events=events,
                max_candidates=max_candidates,
                hint=hint,
                retrieved_reference=retrieved_reference,
            )
        return fn(
            user_id=user_id,
            messages=messages,
            events=events,
            max_candidates=max_candidates,
            hint=hint,
        )

    def add(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        *,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ) -> List[Skill]:
        """Alias of `ingest` kept for ergonomic compatibility."""

        return self.ingest(
            messages=messages,
            events=events,
            user_id=user_id,
            metadata=metadata,
            hint=hint,
        )

    def search(
        self,
        query: str,
        *,
        user_id: str,
        limit: Optional[int] = None,
        scope: Optional[str] = None,  # user|common|library|all
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SkillHit]:
        """
        Retrieves relevant skills for a query.

        Scope behavior:
        - user: only current user's skills
        - library/common: shared skills
        - all: union of user + shared
        """

        merged = dict(filters or {})
        if scope is not None and str(scope).strip():
            merged["scope"] = str(scope).strip()
        return self.store.search(
            user_id=user_id,
            query=query,
            limit=limit or self.config.default_search_limit,
            filters=merged,
        )

    def get(self, skill_id: str) -> Optional[Skill]:
        """Returns a single skill by id, or `None` if not found."""

        return self.store.get(skill_id)

    def get_all(self, *, user_id: str) -> List[Skill]:
        """Legacy alias of `list`."""

        return self.list(user_id=user_id)

    def list(self, *, user_id: str) -> List[Skill]:
        """Lists active user-owned skills."""

        return self.store.list(user_id=user_id)

    def delete(self, skill_id: str) -> bool:
        """Deletes a user-owned skill by id."""

        return self.store.delete(skill_id)

    def upsert(
        self,
        *,
        user_id: str,
        name: str,
        description: str,
        instructions: str,
        triggers: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        examples: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[Dict[str, Any]] = None,
        skill_id: Optional[str] = None,
    ) -> Skill:
        """
        Manual upsert API used by UI/editor flows.

        Unlike `ingest`, this expects already-structured fields and writes the skill directly.
        """

        skill = Skill(
            id=skill_id or str(uuid.uuid4()),
            user_id=user_id,
            name=name.strip(),
            description=description.strip(),
            instructions=instructions.strip(),
            triggers=[t.strip() for t in (triggers or []) if t and t.strip()],
            tags=[t.strip() for t in (tags or []) if t and t.strip()],
            examples=[],
            metadata=metadata or {},
            source=source,
            created_at=now_iso(),
            updated_at=now_iso(),
        )
        if examples:
            from .models import SkillExample

            skill.examples = [
                SkillExample(
                    input=str(e.get("input", "")).strip(),
                    output=(str(e.get("output")).strip() if e.get("output") else None),
                    notes=(str(e.get("notes")).strip() if e.get("notes") else None),
                )
                for e in examples
                if e.get("input")
            ]
        skill.files = build_agent_skill_files(skill)
        self.store.upsert(skill, raw=asdict(skill))
        return skill

    def export_skill_md(self, skill_id: str) -> Optional[str]:
        """Exports a skill as a single `SKILL.md` string."""

        return _export_skill_md(self.store, skill_id)

    def export_skill_dir(self, skill_id: str) -> Optional[Dict[str, str]]:
        """Exports a skill artifact as `{relative_path: file_content}`."""

        return _export_skill_dir(self.store, skill_id)

    def write_skill_dir(self, skill_id: str, *, root_dir: str) -> Optional[str]:
        """Writes one skill artifact to disk and returns the output directory path."""

        return _write_skill_dir(self.store, skill_id, root_dir=root_dir)

    def write_skill_dirs(self, *, user_id: str, root_dir: str) -> List[str]:
        """Writes all user skills to disk as Agent Skill directories."""

        return _write_skill_dirs(self.store, user_id=user_id, root_dir=root_dir)

    def import_agent_skill_dirs(
        self,
        *,
        root_dir: str,
        user_id: str,
        overwrite: bool = True,
        include_files: bool = True,
        max_file_bytes: int = 1_000_000,
        max_depth: int = 6,
        reassign_ids: bool = True,
    ) -> List[Skill]:
        """
        Imports existing Agent Skill directory artifacts (anthropics/skills style) into this store.

        Expected layout:
        - root_dir/**/SKILL.md (recursively scanned)

        The imported skills are upserted into the configured SkillStore (e.g., LocalSkillStore).
        """
        return _import_agent_skill_dirs(
            store=self.store,
            root_dir=root_dir,
            user_id=user_id,
            overwrite=overwrite,
            include_files=include_files,
            max_file_bytes=max_file_bytes,
            max_depth=max_depth,
            reassign_ids=reassign_ids,
        )

    def render_context(
        self,
        query: str,
        *,
        user_id: str,
        limit: Optional[int] = None,
        scope: Optional[str] = None,  # user|common|library|all
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        hits = self.search(query, user_id=user_id, limit=limit, scope=scope, filters=filters)
        skills = [h.skill for h in hits]
        return render_skills_context(
            skills,
            query=query,
            max_chars=self.config.max_context_chars,
        )
