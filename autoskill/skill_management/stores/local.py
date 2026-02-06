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

import hashlib
import os
import re
import shutil
import threading
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ...embeddings.base import EmbeddingModel
from ..formats.agent_skill import load_agent_skill_dir, upsert_skill_md_id
from ...models import Skill, SkillHit, SkillStatus
from ..vectors import FlatFileVectorIndex
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
        users_dirname: str = "Users",
        libraries_dirname: str = "Common",
        library_dirs: Optional[List[Tuple[str, str]]] = None,
        include_libraries: bool = True,
        include_legacy_root: bool = False,
    ) -> None:
        self._embeddings = embeddings
        self._root_dir = os.path.abspath(os.path.expanduser(str(path)))
        self._max_depth = max(0, int(max_depth))
        self._cache_vectors = bool(cache_vectors)
        self._vector_cache_dir = os.path.join(
            self._root_dir, str(vector_cache_dirname).replace("/", os.sep)
        )

        self._users_dirname = str(users_dirname or "Users").strip() or "Users"
        self._libraries_dirname = str(libraries_dirname or "Common").strip() or "Common"
        self._users_root = os.path.join(self._root_dir, self._users_dirname)
        self._libraries_root = os.path.join(self._root_dir, self._libraries_dirname)

        self._library_dirs = list(library_dirs or [])
        self._include_libraries = bool(include_libraries)
        self._include_legacy_root = bool(include_legacy_root)

        self._lock = threading.RLock()
        self._records: Dict[str, _Record] = {}

        os.makedirs(self._root_dir, exist_ok=True)
        if self._cache_vectors:
            self._maybe_migrate_legacy_vector_cache()
            os.makedirs(self._vector_cache_dir, exist_ok=True)
            self._index = FlatFileVectorIndex(
                dir_path=self._vector_cache_dir, name=str(vector_index_name or "skills")
            )
        else:
            self._index = None

        self._load_existing()

    @property
    def path(self) -> str:
        return self._root_dir

    def upsert(self, skill: Skill, *, raw: Optional[Dict[str, Any]] = None) -> None:
        user_id = str(skill.user_id or "").strip() or "default"
        user_root = os.path.join(self._users_root, user_id)
        os.makedirs(user_root, exist_ok=True)

        with self._lock:
            rec = self._records.get(skill.id)
            if rec is not None and rec.scope == "user" and rec.owner == user_id:
                dir_path = rec.dir_path
            else:
                dir_path = self._allocate_dir(skill=skill, base_dir=user_root)

            os.makedirs(dir_path, exist_ok=True)
            self._write_skill_files(skill=skill, dir_path=dir_path)

            vector = self._embed_skill(skill)
            if self._cache_vectors and self._index is not None:
                self._index.upsert(skill.id, vector)
                self._index.save()

            self._records[skill.id] = _Record(
                skill=skill,
                dir_path=dir_path,
                vector=(None if self._cache_vectors else vector),
                scope="user",
                owner=user_id,
            )

    def get(self, skill_id: str) -> Optional[Skill]:
        with self._lock:
            rec = self._records.get(skill_id)
            return rec.skill if rec else None

    def delete(self, skill_id: str) -> bool:
        with self._lock:
            rec = self._records.get(skill_id)
            if rec is None:
                return False
            if rec.scope != "user":
                return False

            self._records.pop(skill_id, None)
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
        filters = filters or {}
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
                self._embed_missing_records(missing2)

            candidates: List[Tuple[float, Skill]] = []
            for rec in filtered_records:
                score = _dot(qvec, rec.vector or [])
                candidates.append((score, rec.skill))

            candidates.sort(key=lambda x: x[0], reverse=True)
            return [SkillHit(skill=s, score=float(sc)) for sc, s in candidates[:limit]]

    def _load_existing(self) -> None:
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
            self._records = loaded

    def _load_library_root(
        self, loaded: Dict[str, _Record], *, library_name: str, library_root: str
    ) -> None:
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

    def _allocate_dir(self, *, skill: Skill, base_dir: str) -> str:
        from ..formats.agent_skill import skill_dir_name

        base = skill_dir_name(skill) or "skill"
        candidate = os.path.join(base_dir, base)

        used_dirs = {
            r.dir_path
            for r in self._records.values()
            if r.scope == "user" and os.path.dirname(r.dir_path) == os.path.abspath(base_dir)
        }
        if candidate not in used_dirs and not os.path.exists(candidate):
            return candidate

        suffix = (skill.id or "")[:8] or _hash_id(skill.id)[:8]
        return os.path.join(base_dir, f"{base}-{suffix}")

    def _write_skill_files(self, *, skill: Skill, dir_path: str) -> None:
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
        return self._embeddings.embed([_skill_to_text(skill)])[0]

    def _embed_missing_records(self, records: List[_Record]) -> None:
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

def _hash_id(skill_id: str) -> str:
    return hashlib.sha256(str(skill_id or "").encode("utf-8")).hexdigest()[:40]
