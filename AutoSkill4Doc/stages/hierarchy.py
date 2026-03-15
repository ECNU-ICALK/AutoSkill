"""
Visible hierarchy browse/retrieve helpers for AutoSkill4Doc.

Fallback order:
1. `.runtime/library_manifest.json`
2. visible family scan
3. runtime registry scan
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..models import SkillSpec, VersionState
from ..store.layout import library_manifest_path, normalize_library_root, safe_family_name, safe_visible_name
from ..store.registry import DocumentRegistry

_TOKEN_RE = re.compile(r"[a-z0-9_]+|[\u4e00-\u9fff]{1,4}", re.IGNORECASE)
_RUNTIME_VISIBLE_STATES = {
    VersionState.CANDIDATE,
    VersionState.DRAFT,
    VersionState.EVALUATING,
    VersionState.ACTIVE,
    VersionState.WATCHLIST,
}


def retrieve_hierarchy(
    *,
    store_root: str,
    profile_id: str = "",
    family_name: str = "",
    query: str = "",
    limit: int = 20,
) -> Dict[str, Any]:
    """Browses or searches the visible hierarchy using manifest-first fallback."""

    root = normalize_library_root(store_root)
    profile_key = str(profile_id or "").strip()
    family_key = str(family_name or "").strip()
    query_text = str(query or "").strip()

    families = _families_from_manifest(root=root, profile_id=profile_key)
    route = "manifest"
    if not families:
        families = _families_from_visible_scan(root=root, family_name=family_key)
        route = "visible_scan"
    if not families:
        families = _families_from_runtime_registry(root=root, family_name=family_key)
        route = "runtime_scan"

    if not families:
        return {
            "route": "not_found",
            "fallback": route,
            "profile_id": profile_key or None,
            "family_name": family_key or None,
            "parent": None,
            "hits": [],
            "families": [],
            "errors": [{"stage": "retrieve_hierarchy", "error": "no family hierarchy found"}],
        }

    if not query_text and not family_key:
        return {
            "route": "family_list",
            "fallback": route,
            "profile_id": profile_key or None,
            "family_name": None,
            "parent": None,
            "hits": [],
            "families": [
                {
                    "family_name": item["family_name"],
                    "relative_root": item.get("relative_root") or item["family_name"],
                    "child_count": len(list(item.get("children") or [])),
                    "parent_relative_path": (item.get("parent") or {}).get("relative_path"),
                }
                for item in families
            ],
            "errors": [],
        }

    chosen = _choose_family_entry(families=families, family_name=family_key, query=query_text)
    if chosen is None:
        return {
            "route": "family_not_found",
            "fallback": route,
            "profile_id": profile_key or None,
            "family_name": family_key or None,
            "parent": None,
            "hits": [],
            "families": [],
            "errors": [{"stage": "retrieve_hierarchy", "error": "requested family was not found"}],
        }

    if not query_text:
        hits = _browse_child_hits(chosen)
        return {
            "route": "family_hierarchy",
            "fallback": route,
            "profile_id": profile_key or None,
            "family_name": chosen["family_name"],
            "parent": dict(chosen.get("parent") or {}),
            "hits": hits[: max(1, int(limit or 20))],
            "families": [],
            "errors": [],
        }

    hits = _search_child_hits(chosen, query=query_text)[: max(1, int(limit or 20))]
    return {
        "route": "query_hits",
        "fallback": route,
        "profile_id": profile_key or None,
        "family_name": chosen["family_name"],
        "parent": dict(chosen.get("parent") or {}),
        "hits": hits,
        "families": [],
        "errors": [],
    }


def _families_from_manifest(*, root: str, profile_id: str) -> List[Dict[str, Any]]:
    path = library_manifest_path(root)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []

    profiles = list(payload.get("profiles") or [])
    if profile_id:
        for profile in profiles:
            if not isinstance(profile, dict):
                continue
            if str(profile.get("profile_id") or "").strip() == profile_id:
                return _normalize_family_entries(list(profile.get("families") or profile.get("schools") or []))
        return []
    families = list(payload.get("families") or payload.get("schools") or [])
    return _normalize_family_entries(families)


def _families_from_visible_scan(*, root: str, family_name: str) -> List[Dict[str, Any]]:
    families: List[Dict[str, Any]] = []
    if not os.path.isdir(root):
        return families
    want_name = str(family_name or "").strip().lower()
    for name in sorted(os.listdir(root)):
        if not name or name.startswith("."):
            continue
        family_dir = os.path.join(root, name)
        if not os.path.isdir(family_dir):
            continue
        if want_name and name.lower() != want_name:
            continue
        parent_relative_path = ""
        parent_path = os.path.join(family_dir, "总技能", "SKILL.md")
        if os.path.isfile(parent_path):
            parent_relative_path = os.path.relpath(parent_path, root).replace(os.sep, "/")
        children: List[Dict[str, Any]] = []
        manifest_path = os.path.join(family_dir, "总技能", "references", "children_manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                raw_children = payload.get("children")
                if isinstance(raw_children, list):
                    children = [dict(item) for item in raw_children if isinstance(item, dict)]
            except Exception:
                children = []
        if not children:
            children_root = os.path.join(family_dir, "子技能")
            if os.path.isdir(children_root):
                for child_name in sorted(os.listdir(children_root)):
                    md_path = os.path.join(children_root, child_name, "SKILL.md")
                    if os.path.isfile(md_path):
                        children.append(
                            {
                                "name": child_name,
                                "description": "",
                                "child_type": "",
                                "taxonomy_class": "",
                                "relative_path": os.path.relpath(md_path, root).replace(os.sep, "/"),
                            }
                        )
        if not children and not parent_relative_path:
            continue
        families.append(
            {
                "family_name": name,
                "relative_root": name,
                "parent": {"name": name, "relative_path": parent_relative_path},
                "children": children,
                "terms": [name],
            }
        )
    return _normalize_family_entries(families)


def _families_from_runtime_registry(*, root: str, family_name: str) -> List[Dict[str, Any]]:
    registry_root = os.path.join(root, ".runtime", "document_registry")
    if not os.path.isdir(registry_root):
        return []
    registry = DocumentRegistry(root_dir=registry_root)
    grouped: Dict[str, List[SkillSpec]] = {}
    for skill in registry.list_skills():
        if skill.status not in _RUNTIME_VISIBLE_STATES:
            continue
        family = _runtime_family_name(skill)
        grouped.setdefault(family, []).append(skill)
    families: List[Dict[str, Any]] = []
    want_name = str(family_name or "").strip().lower()
    for name, skills in sorted(grouped.items(), key=lambda item: item[0].lower()):
        if want_name and name.lower() != want_name:
            continue
        children: List[Dict[str, Any]] = []
        for skill in sorted(skills, key=lambda item: (str(item.name or "").lower(), str(item.skill_id or ""))):
            relative_path = os.path.join(name, "子技能", safe_visible_name(skill.name), "SKILL.md").replace(os.sep, "/")
            children.append(
                {
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "description": skill.description,
                    "child_type": str((skill.metadata or {}).get("child_type") or skill.task_family or ""),
                    "taxonomy_class": str((skill.metadata or {}).get("taxonomy_class") or ""),
                    "relative_path": relative_path,
                    "selector_terms": list(skill.triggers or []) + list(skill.tags or []),
                }
            )
        parent_relative_path = os.path.join(name, "总技能", "SKILL.md").replace(os.sep, "/")
        families.append(
            {
                "family_name": name,
                "relative_root": name,
                "parent": {"name": name, "relative_path": parent_relative_path},
                "children": children,
                "terms": [name],
            }
        )
    return _normalize_family_entries(families)


def _runtime_family_name(skill: SkillSpec) -> str:
    metadata = dict(skill.metadata or {})
    for candidate in [
        str(metadata.get("family_name") or "").strip(),
        str(metadata.get("school_name") or "").strip(),
        str(metadata.get("taxonomy_class") or "").strip(),
        str(skill.domain or "").strip(),
        str(skill.method_family or "").strip(),
        "未分类技能",
    ]:
        if candidate:
            return safe_family_name(candidate)
    return safe_family_name("未分类技能")


def _normalize_family_entries(entries: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for raw in entries or []:
        if not isinstance(raw, dict):
            continue
        family_name = str(raw.get("family_name") or raw.get("school_name") or "").strip() or "未命名家族"
        parent = dict(raw.get("parent") or {})
        children: List[Dict[str, Any]] = []
        for child in list(raw.get("children") or []):
            if not isinstance(child, dict):
                continue
            selector_terms = [str(item).strip() for item in list(child.get("selector_terms") or []) if str(item).strip()]
            children.append(
                {
                    "skill_id": str(child.get("skill_id") or "").strip() or None,
                    "name": str(child.get("name") or "").strip() or "未命名子技能",
                    "description": str(child.get("description") or "").strip(),
                    "child_type": str(child.get("child_type") or "").strip(),
                    "taxonomy_class": str(child.get("taxonomy_class") or "").strip(),
                    "relative_path": str(child.get("relative_path") or "").strip() or None,
                    "selector_terms": selector_terms,
                }
            )
        out.append(
            {
                "family_name": family_name,
                "relative_root": str(raw.get("relative_root") or family_name).strip() or family_name,
                "profile_id": str(raw.get("profile_id") or "").strip(),
                "taxonomy_axis": str(raw.get("taxonomy_axis") or "").strip(),
                "terms": [str(item).strip() for item in list(raw.get("terms") or []) if str(item).strip()] or [family_name],
                "parent": {
                    "name": str(parent.get("name") or family_name).strip() or family_name,
                    "relative_path": str(parent.get("relative_path") or raw.get("parent_relative_path") or "").strip() or None,
                },
                "children": children,
            }
        )
    out.sort(key=lambda item: str(item.get("family_name") or "").lower())
    return out


def _choose_family_entry(*, families: Iterable[Dict[str, Any]], family_name: str, query: str) -> Optional[Dict[str, Any]]:
    family_entries = [dict(entry) for entry in families or [] if isinstance(entry, dict)]
    want_name = str(family_name or "").strip().lower()
    if want_name:
        for entry in family_entries:
            if str(entry.get("family_name") or entry.get("school_name") or "").strip().lower() == want_name:
                return entry
        return None
    query_low = str(query or "").strip().lower()
    best: Optional[Tuple[int, Dict[str, Any]]] = None
    for entry in family_entries:
        score = 0
        for term in list(entry.get("terms") or []):
            token = str(term or "").strip().lower()
            if token and token in query_low:
                score = max(score, len(token))
        if score and (best is None or score > best[0]):
            best = (score, entry)
    if best is not None:
        return best[1]
    return family_entries[0] if family_entries else None


def _browse_child_hits(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "skill_id": child.get("skill_id"),
            "name": child.get("name"),
            "description": child.get("description"),
            "child_type": child.get("child_type"),
            "taxonomy_class": child.get("taxonomy_class"),
            "relative_path": child.get("relative_path"),
            "reason": "browse",
        }
        for child in sorted(list(entry.get("children") or []), key=lambda item: str(item.get("name") or "").lower())
    ]


def _search_child_hits(entry: Dict[str, Any], *, query: str) -> List[Dict[str, Any]]:
    query_tokens = _tokenize(query)
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for child in list(entry.get("children") or []):
        haystack = " ".join(
            [
                str(child.get("name") or ""),
                str(child.get("description") or ""),
                str(child.get("child_type") or ""),
                str(child.get("taxonomy_class") or ""),
                " ".join(list(child.get("selector_terms") or [])),
            ]
        )
        score = _lexical_score(query_tokens, haystack)
        if score <= 0.0:
            continue
        scored.append(
            (
                score,
                {
                    "skill_id": child.get("skill_id"),
                    "name": child.get("name"),
                    "description": child.get("description"),
                    "child_type": child.get("child_type"),
                    "taxonomy_class": child.get("taxonomy_class"),
                    "relative_path": child.get("relative_path"),
                    "score": score,
                    "reason": "query",
                },
            )
        )
    scored.sort(key=lambda item: (-item[0], str(item[1].get("name") or "").lower()))
    return [item[1] for item in scored]


def _tokenize(text: str) -> List[str]:
    return [str(token or "").strip().lower() for token in _TOKEN_RE.findall(str(text or "").lower()) if str(token or "").strip()]


def _lexical_score(query_tokens: List[str], text: str) -> float:
    if not query_tokens:
        return 0.0
    haystack = str(text or "").lower()
    score = 0.0
    for token in query_tokens:
        if token and token in haystack:
            score += max(1.0, float(len(token)) / 4.0)
    return score
