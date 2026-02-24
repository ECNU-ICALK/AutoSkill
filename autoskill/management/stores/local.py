"""
LocalSkillStore: a filesystem-backed SkillStore using one-skill-per-directory artifacts.

Storage layout (recommended):
- store_root/
  - Users/
    - <user_id>/
      - <skill_dir_1>/SKILL.md (+ optional scripts/resources)
      - <skill_dir_2>/SKILL.md
  - Common/
    - <skill_dir_x>/SKILL.md (+ optional scripts/resources)
    - <optional_library_name>/<skill_dir_y>/SKILL.md
  - vectors/  (persistent vector index files)

The store can also load "legacy flat" layouts where skills live directly under `store_root/`.

Notes:
- This store avoids JSON files for persistence.
- Only `SKILL.md` is parsed into memory; bundled resources are left on disk.
- Vectors are cached under `store_root/vectors/` so external libraries do not need to be modified.
"""

from __future__ import annotations

import collections
import os
import re
import shutil
import threading
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ...embeddings.base import EmbeddingModel
from ..formats.agent_skill import load_agent_skill_dir, upsert_skill_md_id
from ..identity import META_IDENTITY_DESC_NORM, identity_desc_norm_from_fields, normalize_identity_text
from ...models import Skill, SkillHit, SkillStatus
from ..vectors import FlatFileVectorIndex, VectorIndex
from .base import SkillStore


def _dot(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return float(sum(x * y for x, y in zip(a, b)))


def _skill_to_text(skill: Skill) -> str:
    triggers = "\n".join(skill.triggers or [])
    tags = " ".join(skill.tags or [])
    return (
        f"Name: {skill.name}\n"
        f"Description: {skill.description}\n"
        f"Instructions: {skill.instructions}\n"
        f"Triggers:\n{triggers}\n"
        f"Tags: {tags}\n"
    )


def _passes_filters(skill: Skill, filters: Dict[str, Any]) -> bool:
    want_tags = filters.get("tags")
    if want_tags:
        want_set = {str(t).strip().lower() for t in want_tags if str(t).strip()}
        have_set = {t.strip().lower() for t in (skill.tags or []) if t.strip()}
        if want_set and not (want_set & have_set):
            return False

    want_status = filters.get("status")
    if want_status and str(skill.status.value) != str(want_status):
        return False

    want_meta = filters.get("metadata")
    if isinstance(want_meta, dict):
        for k, v in want_meta.items():
            if skill.metadata.get(k) != v:
                return False

    return True


def _safe_rel_path(path: str) -> str:
    rel = str(path or "").lstrip("/").replace("\\", "/")
    parts: List[str] = []
    for p in rel.split("/"):
        if not p or p in {".", ".."}:
            continue
        if p.startswith(".."):
            p = p.replace("..", "_")
        parts.append(p)
    return "/".join(parts)


_ID_LINE_RE = re.compile(r"^\s*id\s*:\s*(.*?)\s*$", re.IGNORECASE)


def _skill_md_has_nonempty_id(md: str) -> bool:
    lines = (md or "").splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return False

    for ln in lines[1:end]:
        m = _ID_LINE_RE.match(ln)
        if not m:
            continue
        val = str(m.group(1) or "").strip()
        if not val or val in {'""', "''"}:
            return False
        if val in {">", ">-", "|", "|-"}:
            return False
        return True
    return False


def _iter_skill_dirs(
    base_dir: str,
    *,
    max_depth: int,
    skip_dirnames: Optional[set[str]] = None,
) -> Iterable[Tuple[str, str]]:
    """
    Yields (skill_dir_abs_path, rel_key) for directories containing SKILL.md.
    A skill directory is treated as a leaf (no nested skill scanning under it).
    """

    base_dir = os.path.abspath(os.path.expanduser(str(base_dir)))
    base_sep = base_dir.rstrip(os.sep) + os.sep
    skip_dirnames = set(skip_dirnames or set())

    for current, dirs, files in os.walk(base_dir):
        current_abs = os.path.abspath(current)
        rel = current_abs[len(base_sep) :] if current_abs.startswith(base_sep) else ""
        depth = 0 if not rel else rel.count(os.sep) + 1
        if depth > int(max_depth):
            dirs[:] = []
            continue

        dirs[:] = [
            d
            for d in dirs
            if d
            and not d.startswith(".")
            and d not in {"__pycache__", "node_modules"}
            and d not in skip_dirnames
        ]

        if "SKILL.md" in files:
            rel_key = rel.replace(os.sep, "/") or os.path.basename(current_abs)
            yield current_abs, rel_key
            dirs[:] = []


@dataclass
class _Record:
    skill: Skill
    dir_path: str
    vector: Optional[List[float]] = None
    scope: str = "user"  # user|library
    owner: str = ""  # user_id or library_name


class LocalSkillStore(SkillStore):
    def __init__(
        self,
        *,
        embeddings: EmbeddingModel,
        path: str,
        max_depth: int = 6,
        cache_vectors: bool = True,
        vector_cache_dirname: str = "vectors",
        vector_index_name: str = "skills",
        vector_index: Optional[VectorIndex] = None,
        vector_backend_name: str = "flat",
        users_dirname: str = "Users",
        libraries_dirname: str = "Common",
        library_dirs: Optional[List[Tuple[str, str]]] = None,
        include_libraries: bool = True,
        include_legacy_root: bool = False,
    ) -> None:
        """
        Creates a filesystem-backed skill store with optional persistent vector cache.

        Directory model:
        - user skills: `<root>/Users/<user_id>/<skill_dir>/SKILL.md`
        - shared skills: `<root>/Common/.../SKILL.md`
        - vectors: `<root>/vectors/*`
        """

        self._embeddings = embeddings
        self._root_dir = os.path.abspath(os.path.expanduser(str(path)))
        self._max_depth = max(0, int(max_depth))
        self._cache_vectors = bool(cache_vectors)
        self._vector_cache_dir = os.path.join(
            self._root_dir, str(vector_cache_dirname).replace("/", os.sep)
        )
        self._vector_backend_name = str(vector_backend_name or "").strip().lower()

        self._users_dirname = str(users_dirname or "Users").strip() or "Users"
        self._libraries_dirname = str(libraries_dirname or "Common").strip() or "Common"
        self._users_root = os.path.join(self._root_dir, self._users_dirname)
        self._libraries_root = os.path.join(self._root_dir, self._libraries_dirname)

        self._library_dirs = list(library_dirs or [])
        self._include_libraries = bool(include_libraries)
        self._include_legacy_root = bool(include_legacy_root)

        self._lock = threading.RLock()
        self._records: Dict[str, _Record] = {}
        self._bg_embed_lock = threading.Lock()
        self._bg_embed_pending: set[str] = set()
        self._bg_embed_queue: "collections.deque[str]" = collections.deque()
        self._bg_embed_thread: Optional[threading.Thread] = None
        # O(1) exact dedupe index for user skills by normalized description identity.
        self._identity_desc_index_by_user: Dict[str, Dict[str, set[str]]] = {}
        self._identity_desc_key_by_skill: Dict[str, Tuple[str, str]] = {}

        os.makedirs(self._root_dir, exist_ok=True)
        if self._cache_vectors:
            os.makedirs(self._vector_cache_dir, exist_ok=True)
            if vector_index is not None:
                self._index = vector_index
                if not self._vector_backend_name:
                    self._vector_backend_name = type(vector_index).__name__.lower()
            else:
                self._maybe_migrate_legacy_vector_cache()
                self._index = FlatFileVectorIndex(
                    dir_path=self._vector_cache_dir, name=str(vector_index_name or "skills")
                )
                if not self._vector_backend_name:
                    self._vector_backend_name = "flat"
        else:
            self._index = None
            self._vector_backend_name = "none"

        self._load_existing()

    @property
    def path(self) -> str:
        """Returns the normalized store root path."""

        return self._root_dir

    def upsert(self, skill: Skill, *, raw: Optional[Dict[str, Any]] = None) -> None:
        """
        Upserts one user-owned skill.

        Side effects:
        - writes/updates skill directory files on disk
        - updates vector index (or in-memory vector cache)
        """

        user_id = str(skill.user_id or "").strip() or "default"
        user_root = os.path.join(self._users_root, user_id)
        os.makedirs(user_root, exist_ok=True)

        with self._lock:
            rec = self._records.get(skill.id)
            if rec is not None and rec.scope == "user" and rec.owner == user_id:
                used_dirs = {
                    os.path.abspath(r.dir_path)
                    for sid, r in self._records.items()
                    if sid != skill.id and r.scope == "user" and r.owner == user_id
                }
                old_dir = os.path.abspath(rec.dir_path)
                dir_path = self._allocate_dir(
                    skill=skill,
                    base_dir=user_root,
                    used_dirs=used_dirs,
                    exclude_dir=old_dir,
                )
                if dir_path != old_dir:
                    try:
                        if os.path.isdir(old_dir):
                            os.makedirs(os.path.dirname(dir_path), exist_ok=True)
                            shutil.move(old_dir, dir_path)
                        elif not os.path.exists(dir_path):
                            os.makedirs(dir_path, exist_ok=True)
                    except Exception:
                        dir_path = old_dir
            else:
                used_dirs = {
                    os.path.abspath(r.dir_path)
                    for r in self._records.values()
                    if r.scope == "user" and r.owner == user_id
                }
                dir_path = self._allocate_dir(skill=skill, base_dir=user_root, used_dirs=used_dirs)

            os.makedirs(dir_path, exist_ok=True)
            self._write_skill_files(skill=skill, dir_path=dir_path)

            vector = self._embed_skill(skill)
            if self._cache_vectors and self._index is not None:
                self._index.upsert(skill.id, vector)
                self._index.save()

            self._deindex_identity_desc_locked(skill.id)
            self._records[skill.id] = _Record(
                skill=skill,
                dir_path=dir_path,
                vector=(None if self._cache_vectors else vector),
                scope="user",
                owner=user_id,
            )
            self._index_identity_desc_locked(self._records[skill.id])

    def get(self, skill_id: str) -> Optional[Skill]:
        """Returns a skill by id if loaded in memory."""

        with self._lock:
            rec = self._records.get(skill_id)
            return rec.skill if rec else None

    def delete(self, skill_id: str) -> bool:
        """Deletes one user-owned skill directory and associated vector record."""

        with self._lock:
            rec = self._records.get(skill_id)
            if rec is None:
                return False
            if rec.scope != "user":
                return False

            self._records.pop(skill_id, None)
            self._deindex_identity_desc_locked(skill_id)
            try:
                shutil.rmtree(rec.dir_path)
            except Exception:
                pass
            if self._cache_vectors and self._index is not None:
                try:
                    if self._index.delete(skill_id):
                        self._index.save()
                except Exception:
                    pass
            return True

    def list(self, *, user_id: str) -> List[Skill]:
        """Lists active skills for a given user id."""

        uid = str(user_id or "").strip()
        with self._lock:
            return [
                r.skill
                for r in self._records.values()
                if r.scope == "user"
                and r.owner == uid
                and r.skill.status != SkillStatus.ARCHIVED
            ]

    def search(
        self,
        *,
        user_id: str,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SkillHit]:
        """
        Searches relevant skills by vector similarity.

        Behavior notes:
        - supports `scope` filters (`user` / `library` / `all`)
        - supports `allow_partial_vectors` for low-latency first query
        - auto-resets vector index when embedding dimensions change
        """

        filters = filters or {}
        allow_partial_vectors = bool(filters.get("allow_partial_vectors", False))
        scope = str(filters.get("scope") or "").strip().lower()  # user|library|all
        if scope in {"common", "shared"}:
            scope = "library"
        want_ids_raw = filters.get("ids")
        if want_ids_raw is None:
            want_id_set = None
        else:
            if isinstance(want_ids_raw, (list, tuple, set)):
                want_ids = list(want_ids_raw)
            else:
                want_ids = [want_ids_raw]
            want_id_set = {str(x).strip() for x in want_ids if str(x).strip()} or None
        uid = str(user_id or "").strip()
        qvec = self._embeddings.embed([query])[0]
        qdims = len(qvec or [])

        with self._lock:
            candidate_records: List[_Record] = []
            for rec in self._records.values():
                if rec.skill.status == SkillStatus.ARCHIVED:
                    continue
                if want_id_set is not None and rec.skill.id not in want_id_set:
                    continue
                if scope == "user":
                    if rec.scope != "user" or rec.owner != uid:
                        continue
                elif scope == "library":
                    if rec.scope != "library":
                        continue
                else:
                    if rec.scope == "user" and rec.owner == uid:
                        candidate_records.append(rec)
                        continue
                    if self._include_libraries and rec.scope == "library":
                        candidate_records.append(rec)
                        continue
                    continue
                candidate_records.append(rec)

            filtered_records: List[_Record] = [
                r for r in candidate_records if _passes_filters(r.skill, filters)
            ]
            if not filtered_records:
                return []

            # Persistent vector index path (recommended).
            if self._cache_vectors and self._index is not None:
                if qdims and self._index.dims is not None and int(self._index.dims) != int(qdims):
                    self._index.reset(dims=qdims)
                    self._index.save()

                missing = [r for r in filtered_records if not self._index.has(r.skill.id)]
                if missing:
                    if allow_partial_vectors:
                        self._schedule_embed_records(missing)
                    else:
                        self._embed_missing_records(missing)
                        self._index.save()

                keys = [r.skill.id for r in filtered_records]
                ranked = self._index.search(qvec, keys=keys, top_k=int(limit))
                hits: List[SkillHit] = []
                for sid, score in ranked:
                    rec2 = self._records.get(sid)
                    if rec2 is None:
                        continue
                    hits.append(SkillHit(skill=rec2.skill, score=float(score)))
                return hits

            # Fallback: in-memory scan (no persistent vector index).
            missing2 = [
                r for r in filtered_records if r.vector is None or (qdims and len(r.vector) != qdims)
            ]
            if missing2:
                if allow_partial_vectors:
                    self._schedule_embed_records(missing2)
                else:
                    self._embed_missing_records(missing2)

            candidates: List[Tuple[float, Skill]] = []
            for rec in filtered_records:
                score = _dot(qvec, rec.vector or [])
                candidates.append((score, rec.skill))

            candidates.sort(key=lambda x: x[0], reverse=True)
            return [SkillHit(skill=s, score=float(sc)) for sc, s in candidates[:limit]]

    def schedule_vector_prewarm(self, *, user_id: str, scope: str = "all") -> int:
        """
        Schedules background vectorization for skills in the given scope.

        This is a best-effort prewarm API for interactive use-cases where first-query latency
        should remain low while vectors are built progressively in the background.
        """

        scope_s = str(scope or "all").strip().lower()
        if scope_s in {"common", "shared"}:
            scope_s = "library"
        uid = str(user_id or "").strip()
        with self._lock:
            records = self._collect_records_for_scope_locked(user_id=uid, scope=scope_s)
            if not records:
                return 0
        return self._schedule_embed_records(records)

    def vector_status(self, *, user_id: str, scope: str = "all") -> Dict[str, Any]:
        """Returns vector index coverage for one user/scope view."""

        scope_s = str(scope or "all").strip().lower()
        if scope_s in {"common", "shared"}:
            scope_s = "library"
        uid = str(user_id or "").strip()

        with self._lock:
            records = self._collect_records_for_scope_locked(user_id=uid, scope=scope_s)
            total = len(records)
            if self._cache_vectors and self._index is not None:
                indexed = sum(1 for r in records if self._index.has(r.skill.id))
                dims = self._index.dims
            else:
                indexed = sum(1 for r in records if r.vector is not None)
                dims = len(records[0].vector or []) if records and records[0].vector else None

        with self._bg_embed_lock:
            pending = sum(
                1
                for r in records
                if str(getattr(r.skill, "id", "") or "").strip() in self._bg_embed_pending
            )

        return {
            "scope": scope_s,
            "user": uid,
            "total_skills": int(total),
            "indexed_skills": int(indexed),
            "missing_skills": int(max(0, total - indexed)),
            "pending_skills": int(pending),
            "dims": (int(dims) if dims is not None else None),
            "cache_dir": (self._vector_cache_dir if self._cache_vectors else ""),
            "cache_enabled": bool(self._cache_vectors),
            "backend": str(self._vector_backend_name or "flat"),
        }

    def rebuild_vectors(
        self,
        *,
        user_id: str,
        scope: str = "all",
        force: bool = False,
        blocking: bool = True,
    ) -> int:
        """
        Rebuilds vectors for the given scope and returns affected record count.

        - `force=False`: embeds only missing vectors.
        - `force=True`: clears existing vectors first, then re-embeds.
        """

        scope_s = str(scope or "all").strip().lower()
        if scope_s in {"common", "shared"}:
            scope_s = "library"
        uid = str(user_id or "").strip()

        with self._lock:
            records = self._collect_records_for_scope_locked(user_id=uid, scope=scope_s)
            if not records:
                return 0

            if self._cache_vectors and self._index is not None:
                if force:
                    if scope_s == "all":
                        self._index.reset(dims=None)
                    else:
                        for rec in records:
                            self._index.delete(rec.skill.id)
                    self._index.save()
                missing = records if force else [r for r in records if not self._index.has(r.skill.id)]
            else:
                if force:
                    for rec in records:
                        rec.vector = None
                missing = records if force else [r for r in records if r.vector is None]

            if not missing:
                return 0

            if not blocking:
                return int(self._schedule_embed_records(missing))

            self._embed_missing_records(missing)
            if self._cache_vectors and self._index is not None:
                self._index.save()
            return int(len(missing))

    def _collect_records_for_scope_locked(self, *, user_id: str, scope: str) -> List[_Record]:
        """
        Collects records for a scope.

        Must be called with `_lock` already held.
        """

        scope_s = str(scope or "all").strip().lower()
        uid = str(user_id or "").strip()
        out: List[_Record] = []
        for rec in self._records.values():
            if rec.skill.status == SkillStatus.ARCHIVED:
                continue
            if scope_s == "user":
                if rec.scope == "user" and rec.owner == uid:
                    out.append(rec)
                continue
            if scope_s == "library":
                if rec.scope == "library":
                    out.append(rec)
                continue
            if rec.scope == "user" and rec.owner == uid:
                out.append(rec)
                continue
            if self._include_libraries and rec.scope == "library":
                out.append(rec)
        return out

    def _load_existing(self) -> None:
        """
        Loads all discoverable skills into memory at startup.

        Loading order:
        1) shared skills under `<root>/Common`
        2) external read-only libraries configured by `library_dirs`
        3) optional legacy flat layout under `<root>`
        4) user skills under `<root>/Users/<user_id>`
        """

        loaded: Dict[str, _Record] = {}

        # 1) Load shared common skills under store_root/Common/... (read-only).
        # Support both:
        # - Common/<skill>/SKILL.md (flat common library)
        # - Common/<library>/<skill>/SKILL.md (multiple grouped libraries)
        if os.path.isdir(self._libraries_root):
            common_owner = str(self._libraries_dirname or "Common").strip() or "Common"
            for name in sorted(os.listdir(self._libraries_root)):
                if not name or name.startswith("."):
                    continue
                entry_root = os.path.join(self._libraries_root, name)
                if not os.path.isdir(entry_root):
                    continue
                if os.path.isfile(os.path.join(entry_root, "SKILL.md")):
                    # Direct common skill directory: Common/<skill>/SKILL.md
                    try:
                        skill = load_agent_skill_dir(
                            entry_root,
                            user_id=f"library:{common_owner}",
                            include_files=False,
                            deterministic_id_key=name,
                        )
                    except Exception:
                        continue
                    self._maybe_persist_missing_id(entry_root, skill_id=skill.id)
                    loaded[skill.id] = _Record(
                        skill=skill,
                        dir_path=entry_root,
                        vector=None,
                        scope="library",
                        owner=common_owner,
                    )
                else:
                    # Grouped library under Common/<library>/...
                    self._load_library_root(
                        loaded, library_name=name, library_root=entry_root
                    )

        # 2) Load additional external library roots (read-only).
        for name, lib_root in (self._library_dirs or []):
            name_s = str(name or "").strip() or os.path.basename(str(lib_root or "").rstrip("/")) or "library"
            root_s = os.path.abspath(os.path.expanduser(str(lib_root)))
            if not os.path.isdir(root_s):
                continue
            self._load_library_root(loaded, library_name=name_s, library_root=root_s)

        # 3) Load legacy skills stored directly under store_root/ (flat layout).
        if self._include_legacy_root and os.path.isdir(self._root_dir):
            # Avoid walking persistent cache directories when scanning legacy flat layouts.
            skip = {self._users_dirname, self._libraries_dirname, ".autoskill", "vectors"}
            for dir_path, rel_key in _iter_skill_dirs(
                self._root_dir, max_depth=self._max_depth, skip_dirnames=skip
            ):
                try:
                    skill = load_agent_skill_dir(
                        dir_path,
                        user_id="library:legacy",
                        include_files=False,
                        deterministic_id_key=f"legacy/{rel_key}",
                    )
                except Exception:
                    continue
                self._maybe_persist_missing_id(dir_path, skill_id=skill.id)
                loaded[skill.id] = _Record(
                    skill=skill,
                    dir_path=dir_path,
                    vector=None,
                    scope="library",
                    owner="legacy",
                )

        # 4) Load user skills under store_root/users/<user_id>/...
        if os.path.isdir(self._users_root):
            for uid in sorted(os.listdir(self._users_root)):
                if not uid or uid.startswith("."):
                    continue
                user_root = os.path.join(self._users_root, uid)
                if not os.path.isdir(user_root):
                    continue
                for dir_path, rel_key in _iter_skill_dirs(user_root, max_depth=self._max_depth):
                    try:
                        skill = load_agent_skill_dir(
                            dir_path,
                            user_id=uid,
                            include_files=False,
                            deterministic_id_key=rel_key,
                        )
                    except Exception:
                        continue
                    self._maybe_persist_missing_id(dir_path, skill_id=skill.id)
                    loaded[skill.id] = _Record(
                        skill=skill,
                        dir_path=dir_path,
                        vector=None,
                        scope="user",
                        owner=uid,
                    )

        with self._lock:
            self._normalize_loaded_user_dirs(loaded)
            self._records = loaded
            self._rebuild_identity_desc_index_locked()

    def _normalize_loaded_user_dirs(self, loaded: Dict[str, _Record]) -> None:
        """
        Normalizes user skill directory names to text-based slugs.

        This keeps historical stores consistent when older runs created id-like folder names.
        """

        grouped: Dict[str, List[_Record]] = {}
        for rec in loaded.values():
            if rec.scope != "user":
                continue
            owner = str(rec.owner or "").strip()
            if not owner:
                continue
            grouped.setdefault(owner, []).append(rec)

        for owner, records in grouped.items():
            user_root = os.path.join(self._users_root, owner)
            os.makedirs(user_root, exist_ok=True)
            used_dirs: set[str] = set()

            # Stable order makes renaming deterministic across runs.
            ordered = sorted(
                records,
                key=lambda r: (
                    str(getattr(r.skill, "name", "") or "").strip().lower(),
                    str(getattr(r.skill, "id", "") or "").strip(),
                ),
            )

            for rec in ordered:
                old_dir = os.path.abspath(str(rec.dir_path or ""))
                new_dir = self._allocate_dir(
                    skill=rec.skill,
                    base_dir=user_root,
                    used_dirs=used_dirs,
                    exclude_dir=old_dir,
                )
                if old_dir and os.path.abspath(new_dir) != old_dir:
                    try:
                        if os.path.isdir(old_dir):
                            os.makedirs(os.path.dirname(new_dir), exist_ok=True)
                            shutil.move(old_dir, new_dir)
                        elif not os.path.exists(new_dir):
                            os.makedirs(new_dir, exist_ok=True)
                    except Exception:
                        new_dir = old_dir
                rec.dir_path = os.path.abspath(new_dir)
                used_dirs.add(rec.dir_path)

    def _load_library_root(
        self, loaded: Dict[str, _Record], *, library_name: str, library_root: str
    ) -> None:
        """Loads one library root into memory as read-only records."""

        lib_name = str(library_name or "library").strip() or "library"
        root = os.path.abspath(os.path.expanduser(str(library_root)))
        for dir_path, rel_key in _iter_skill_dirs(root, max_depth=self._max_depth):
            try:
                skill = load_agent_skill_dir(
                    dir_path,
                    user_id=f"library:{lib_name}",
                    include_files=False,
                    deterministic_id_key=f"{lib_name}/{rel_key}",
                )
            except Exception:
                continue
            self._maybe_persist_missing_id(dir_path, skill_id=skill.id)
            loaded[skill.id] = _Record(
                skill=skill,
                dir_path=dir_path,
                vector=None,
                scope="library",
                owner=lib_name,
            )

    def find_user_skills_by_identity_desc_norm(
        self, *, user_id: str, desc_norm: str, limit: int = 8
    ) -> List[Skill]:
        """
        Returns user skills that share the same normalized description identity.

        Complexity:
        - average O(1) bucket lookup + O(k) output materialization
        """

        uid = str(user_id or "").strip()
        key = normalize_identity_text(desc_norm)
        if not uid or not key:
            return []
        lim = max(1, int(limit or 8))
        with self._lock:
            bucket = self._identity_desc_index_by_user.get(uid, {}).get(key, set())
            if not bucket:
                return []
            out: List[Skill] = []
            for sid in bucket:
                rec = self._records.get(str(sid))
                if rec is None:
                    continue
                if rec.scope != "user" or rec.owner != uid:
                    continue
                if rec.skill.status == SkillStatus.ARCHIVED:
                    continue
                out.append(rec.skill)
            out.sort(key=lambda s: (str(getattr(s, "updated_at", "") or ""), str(getattr(s, "id", "") or "")), reverse=True)
            return out[:lim]

    def _maybe_persist_missing_id(self, dir_path: str, *, skill_id: str) -> None:
        """
        Ensures a store-owned SKILL.md contains a stable `id:` field.

        External library directories passed via `library_dirs` are treated as read-only and are not
        modified unless they are under the store root directory.
        """

        abs_dir = os.path.abspath(os.path.expanduser(str(dir_path)))
        root = self._root_dir.rstrip(os.sep) + os.sep
        if not (abs_dir == self._root_dir or abs_dir.startswith(root)):
            return
        md_path = os.path.join(abs_dir, "SKILL.md")
        if not os.path.isfile(md_path):
            return
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                md = f.read()
            if _skill_md_has_nonempty_id(md):
                return
            updated = upsert_skill_md_id(md, skill_id=str(skill_id))
            if not updated or updated == md:
                return
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(updated)
        except Exception:
            return

    def _identity_desc_norm_for_skill(self, skill: Skill) -> str:
        md = dict(getattr(skill, "metadata", {}) or {})
        from_md = normalize_identity_text(str(md.get(META_IDENTITY_DESC_NORM) or ""))
        if from_md:
            return from_md
        return identity_desc_norm_from_fields(
            description=str(getattr(skill, "description", "") or ""),
            name=str(getattr(skill, "name", "") or ""),
        )

    def _rebuild_identity_desc_index_locked(self) -> None:
        self._identity_desc_index_by_user = {}
        self._identity_desc_key_by_skill = {}
        for rec in self._records.values():
            self._index_identity_desc_locked(rec)

    def _deindex_identity_desc_locked(self, skill_id: str) -> None:
        sid = str(skill_id or "").strip()
        if not sid:
            return
        prev = self._identity_desc_key_by_skill.pop(sid, None)
        if not prev:
            return
        uid, key = prev
        by_user = self._identity_desc_index_by_user.get(uid)
        if not by_user:
            return
        bucket = by_user.get(key)
        if not bucket:
            return
        bucket.discard(sid)
        if not bucket:
            by_user.pop(key, None)
        if not by_user:
            self._identity_desc_index_by_user.pop(uid, None)

    def _index_identity_desc_locked(self, rec: _Record) -> None:
        if rec.scope != "user":
            return
        uid = str(rec.owner or "").strip()
        sid = str(getattr(rec.skill, "id", "") or "").strip()
        if not uid or not sid:
            return
        key = self._identity_desc_norm_for_skill(rec.skill)
        if not key:
            return
        self._identity_desc_key_by_skill[sid] = (uid, key)
        by_user = self._identity_desc_index_by_user.setdefault(uid, {})
        by_user.setdefault(key, set()).add(sid)

    def _maybe_migrate_legacy_vector_cache(self) -> None:
        """
        Best-effort migration from the legacy cache path:
          store_root/.autoskill/vectors -> store_root/vectors

        This preserves existing vector indices so switching to the new default does not trigger
        unnecessary re-embedding.
        """

        try:
            new_dir = os.path.abspath(self._vector_cache_dir)
            legacy_dir = os.path.join(self._root_dir, ".autoskill", "vectors")
            legacy_dir = os.path.abspath(legacy_dir)
            if new_dir == legacy_dir:
                return
            if not os.path.isdir(legacy_dir):
                return
            if os.path.isdir(new_dir):
                try:
                    if any(os.scandir(new_dir)):
                        return
                except Exception:
                    return
            os.makedirs(new_dir, exist_ok=True)
            for name in os.listdir(legacy_dir):
                src = os.path.join(legacy_dir, name)
                dst = os.path.join(new_dir, name)
                if not os.path.isfile(src):
                    continue
                if os.path.exists(dst):
                    continue
                try:
                    shutil.copy2(src, dst)
                except Exception:
                    continue
        except Exception:
            return

    def _allocate_dir(
        self,
        *,
        skill: Skill,
        base_dir: str,
        used_dirs: Optional[set[str]] = None,
        exclude_dir: str = "",
    ) -> str:
        """
        Allocates a stable skill directory path under a user root.

        If slug collision happens, appends a numeric suffix (`-2`, `-3`, ...).
        """

        from ..formats.agent_skill import skill_dir_name

        base = skill_dir_name(skill) or "skill"
        base_dir_abs = os.path.abspath(base_dir)
        exclude_abs = os.path.abspath(exclude_dir) if str(exclude_dir or "").strip() else ""
        if used_dirs is None:
            used_set = {
                os.path.abspath(r.dir_path)
                for r in self._records.values()
                if r.scope == "user" and os.path.dirname(os.path.abspath(r.dir_path)) == base_dir_abs
            }
        else:
            used_set = {os.path.abspath(p) for p in used_dirs if str(p or "").strip()}

        def _is_taken(path: str) -> bool:
            p_abs = os.path.abspath(path)
            if exclude_abs and p_abs == exclude_abs:
                return False
            if p_abs in used_set:
                return True
            return os.path.exists(path)

        candidate = os.path.join(base_dir, base)
        if not _is_taken(candidate):
            return candidate

        i = 2
        while True:
            nxt = os.path.join(base_dir, f"{base}-{i}")
            if not _is_taken(nxt):
                return nxt
            i += 1

    def _write_skill_files(self, *, skill: Skill, dir_path: str) -> None:
        """
        Writes all artifact files for one skill.

        `SKILL.md` is always ensured; additional files are written as relative safe paths.
        """

        from ..formats.agent_skill import build_agent_skill_files

        files = dict(skill.files or {})
        if "SKILL.md" not in files or not str(files.get("SKILL.md") or "").strip():
            files.update(build_agent_skill_files(skill))

        for rel_path, content in files.items():
            rel = _safe_rel_path(str(rel_path))
            if not rel:
                continue
            abs_path = os.path.join(dir_path, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(str(content or ""))

    def _embed_skill(self, skill: Skill) -> List[float]:
        """Embeds one skill record into its retrieval text representation."""

        return self._embeddings.embed([_skill_to_text(skill)])[0]

    def _embed_missing_records(self, records: List[_Record]) -> None:
        """Batch-embeds missing vectors and writes results to cache/index."""

        batch_size = 32
        skills = [r.skill for r in records]
        texts = [_skill_to_text(s) for s in skills]

        for i in range(0, len(texts), batch_size):
            chunk_texts = texts[i : i + batch_size]
            chunk_skills = skills[i : i + batch_size]
            vectors = self._embeddings.embed(chunk_texts)
            for s, v in zip(chunk_skills, vectors):
                rec = self._records.get(s.id)
                if rec is None:
                    continue
                vec = [float(x) for x in v]
                if self._cache_vectors and self._index is not None:
                    self._index.upsert(s.id, vec)
                else:
                    rec.vector = vec

    def _schedule_embed_records(self, records: List[_Record]) -> int:
        """
        Schedules missing vectors for asynchronous embedding.

        Returns how many unique skill IDs were newly scheduled.
        """

        queued = 0
        with self._bg_embed_lock:
            for rec in records or []:
                sid = str(getattr(rec.skill, "id", "") or "").strip()
                if not sid:
                    continue
                if sid in self._bg_embed_pending:
                    continue
                self._bg_embed_pending.add(sid)
                self._bg_embed_queue.append(sid)
                queued += 1
            self._ensure_bg_embed_worker_locked()
        return queued

    def _ensure_bg_embed_worker_locked(self) -> None:
        """Starts background embedding worker if no worker is currently alive."""

        t = self._bg_embed_thread
        if t is not None and t.is_alive():
            return
        t2 = threading.Thread(target=self._background_embed_worker, daemon=True)
        self._bg_embed_thread = t2
        t2.start()

    def _background_embed_worker(self) -> None:
        """
        Background embedding loop.

        Pulls queued ids, skips already-embedded records, and persists newly produced vectors.
        """

        batch_size = 32
        while True:
            with self._bg_embed_lock:
                if not self._bg_embed_queue:
                    self._bg_embed_thread = None
                    return
                batch_ids: List[str] = []
                while self._bg_embed_queue and len(batch_ids) < batch_size:
                    sid = str(self._bg_embed_queue.popleft() or "").strip()
                    if sid:
                        batch_ids.append(sid)
            if not batch_ids:
                continue

            work: List[Tuple[str, str]] = []
            with self._lock:
                for sid in batch_ids:
                    rec = self._records.get(sid)
                    if rec is None:
                        continue
                    if self._cache_vectors and self._index is not None:
                        if self._index.has(sid):
                            continue
                    else:
                        if rec.vector is not None:
                            continue
                    work.append((sid, _skill_to_text(rec.skill)))

            if not work:
                self._mark_embed_done(batch_ids)
                continue

            try:
                vectors = self._embeddings.embed([txt for _, txt in work])
            except Exception:
                self._mark_embed_done(batch_ids)
                continue

            with self._lock:
                changed = False
                for (sid, _txt), vec in zip(work, vectors):
                    rec = self._records.get(sid)
                    if rec is None:
                        continue
                    vec_f = [float(x) for x in vec]
                    if self._cache_vectors and self._index is not None:
                        self._index.upsert(sid, vec_f)
                        changed = True
                    else:
                        rec.vector = vec_f
                if changed and self._index is not None:
                    self._index.save()

            self._mark_embed_done(batch_ids)

    def _mark_embed_done(self, ids: List[str]) -> None:
        """Marks queued ids as completed so they can be rescheduled if needed later."""

        with self._bg_embed_lock:
            for sid in ids or []:
                sid_s = str(sid or "").strip()
                if sid_s:
                    self._bg_embed_pending.discard(sid_s)
