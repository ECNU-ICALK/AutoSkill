"""
Visible parent/child skill tree writer for AutoSkill4Doc.

This module does not replace the existing document registry or AutoSkill store.
It adds a human-browsable layer under the document skill library root:

<store_root>/
  <family_name>/
    总技能/
      SKILL.md
      references/
        children_manifest.json
        children_map.md
    子技能/
      <child_name>/
        SKILL.md
        references/
          evidence.md
          evidence_manifest.json

The implementation is intentionally minimal and derives this visible tree from
the current registry state plus run metadata such as `family_name`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import shutil
import uuid
from typing import Any, Dict, List, Optional, Sequence, Tuple

from autoskill.management.formats.agent_skill import render_skill_md
from autoskill.models import Skill, SkillStatus
from autoskill.utils.time import now_iso

from ..core.common import StageLogger, dedupe_strings, emit_stage_log, normalize_text
from ..core.config import DEFAULT_DOC_SKILL_USER_ID
from ..models import DocumentRecord, SkillSpec, SupportRecord, VersionState
from .layout import (
    family_children_visible_root,
    family_parent_visible_root,
    family_visible_root,
    safe_family_name,
    safe_visible_name,
)
from .registry import DocumentRegistry

_VISIBLE_STATES = {
    VersionState.CANDIDATE,
    VersionState.DRAFT,
    VersionState.EVALUATING,
    VersionState.ACTIVE,
    VersionState.WATCHLIST,
}

_ROOT_SKIP_DIRS = {
    ".runtime",
    "Users",
    "Common",
    "vectors",
    "index",
    "__pycache__",
}

@dataclass
class VisibleTreeSyncResult:
    """Compact summary of one visible-tree synchronization run."""

    store_root: str = ""
    affected_families: List[str] = field(default_factory=list)
    parent_paths: List[str] = field(default_factory=list)
    child_paths: List[str] = field(default_factory=list)
    library_manifest_path: str = ""
    readme_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Returns a plain JSON-safe summary."""

        return {
            "store_root": self.store_root,
            "affected_families": list(self.affected_families or []),
            "parent_paths": list(self.parent_paths or []),
            "child_paths": list(self.child_paths or []),
            "library_manifest_path": self.library_manifest_path,
            "readme_path": self.readme_path,
        }


def sync_visible_skill_tree(
    *,
    registry: DocumentRegistry,
    store_root: str,
    documents: Sequence[DocumentRecord],
    support_records: Sequence[SupportRecord],
    skill_specs: Sequence[SkillSpec],
    user_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    store_skills: Optional[Sequence[Skill]] = None,
    logger: StageLogger = None,
) -> VisibleTreeSyncResult:
    """
    Synchronizes the visible parent/child skill tree for affected families.

    The tree is derived from the persisted registry state so updates, merges, and
    deprecations can refresh the visible output consistently.
    """

    root_dir = os.path.abspath(os.path.expanduser(str(store_root or "").strip()))
    if not root_dir:
        return VisibleTreeSyncResult()
    os.makedirs(root_dir, exist_ok=True)

    metadata_map = dict(metadata or {})
    registry_documents = {doc.doc_id: doc for doc in registry.list_documents()}
    for document in documents or []:
        registry_documents[document.doc_id] = document

    registry_supports = {support.support_id: support for support in registry.list_supports()}
    for support in support_records or []:
        registry_supports[support.support_id] = support

    registry_skills = list(registry.list_skills())
    families = _affected_families(registry_skills=registry_skills, skill_specs=skill_specs, metadata=metadata_map)
    result = VisibleTreeSyncResult(store_root=root_dir, affected_families=families)

    explicit_family = str(metadata_map.get("family_name") or metadata_map.get("school_name") or "").strip()
    for family_name in families:
        family_dir = family_visible_root(base_store_root=root_dir, family_name=family_name)
        family_skills = [
            skill
            for skill in registry_skills
            if _family_name_for_skill(skill, metadata=metadata_map) == family_name and skill.status in _VISIBLE_STATES
        ]
        projected_store_skills = _select_store_skills_for_family(
            store_skills=store_skills,
            family_name=family_name,
            explicit_family=explicit_family,
            registry_family_skills=family_skills,
        )
        if os.path.isdir(family_dir):
            shutil.rmtree(family_dir)
        if not family_skills and not projected_store_skills:
            emit_stage_log(logger, f"[visible_tree] remove family={family_name} (no active child skills)")
            continue
        if projected_store_skills:
            child_paths, parent_path = _write_family_tree_from_store(
                family_name=family_name,
                family_dir=family_dir,
                store_skills=projected_store_skills,
                registry_skills=family_skills,
                docs_by_id=registry_documents,
                supports_by_id=registry_supports,
                user_id=user_id,
                metadata=metadata_map,
            )
        else:
            child_paths, parent_path = _write_family_tree(
                family_name=family_name,
                family_dir=family_dir,
                skills=family_skills,
                docs_by_id=registry_documents,
                supports_by_id=registry_supports,
                user_id=user_id,
                metadata=metadata_map,
            )
        result.child_paths.extend(child_paths)
        if parent_path:
            result.parent_paths.append(parent_path)
        emit_stage_log(
            logger,
            f"[visible_tree] family={family_name} children={len(child_paths)} parent={'1' if parent_path else '0'}",
        )

    manifest = _scan_library_manifest(root_dir)
    library_manifest_path = _write_json(
        os.path.join(root_dir, ".runtime", "library_manifest.json"),
        manifest,
    )
    readme_path = _write_text(os.path.join(root_dir, "README.md"), _render_library_readme(manifest))
    result.library_manifest_path = library_manifest_path
    result.readme_path = readme_path
    return result


def _select_store_skills_for_family(
    *,
    store_skills: Optional[Sequence[Skill]],
    family_name: str,
    explicit_family: str,
    registry_family_skills: Sequence[SkillSpec],
) -> List[Skill]:
    """Selects store-final skills that should be projected into one family tree."""

    skills = [skill for skill in list(store_skills or []) if isinstance(skill, Skill)]
    if not skills:
        return []
    if explicit_family:
        return skills
    if len({str(_family_name_for_skill(skill, metadata={}) or "").strip() for skill in registry_family_skills}) <= 1:
        return skills
    return []


def _affected_families(
    *,
    registry_skills: Sequence[SkillSpec],
    skill_specs: Sequence[SkillSpec],
    metadata: Dict[str, Any],
) -> List[str]:
    explicit = str(metadata.get("family_name") or metadata.get("school_name") or "").strip()
    if explicit:
        return [safe_family_name(explicit)]
    names: List[str] = []
    for skill in skill_specs or []:
        names.append(_family_name_for_skill(skill, metadata=metadata))
    if names:
        return dedupe_strings(names, lower=False)
    for skill in registry_skills or []:
        names.append(_family_name_for_skill(skill, metadata=metadata))
    return dedupe_strings(names, lower=False)


def _family_name_for_skill(skill: SkillSpec, *, metadata: Dict[str, Any]) -> str:
    skill_metadata = dict(getattr(skill, "metadata", {}) or {})
    candidates = [
        str(skill_metadata.get("family_name") or "").strip(),
        str(skill_metadata.get("school_name") or "").strip(),
        str(metadata.get("family_name") or "").strip(),
        str(metadata.get("school_name") or "").strip(),
        str(skill_metadata.get("taxonomy_class") or "").strip(),
        str(skill.domain or "").strip(),
        str(skill.method_family or "").strip(),
        "未分类技能",
    ]
    for candidate in candidates:
        if str(candidate or "").strip():
            return safe_family_name(candidate)
    return safe_family_name("未分类技能")


def _child_type_for_skill(skill: SkillSpec) -> str:
    skill_metadata = dict(skill.metadata or {})
    raw = str(skill_metadata.get("child_type") or "").strip()
    return raw or str(skill.task_family or "").strip() or str(skill.asset_type or "").strip()


def _taxonomy_class_for_skill(skill: SkillSpec, *, family_name: str) -> str:
    skill_metadata = dict(skill.metadata or {})
    raw = str(skill_metadata.get("taxonomy_class") or "").strip()
    return raw or family_name


def _selector_terms_for_skill(skill: SkillSpec) -> List[str]:
    return dedupe_strings(
        list(skill.triggers or [])
        + list(skill.tags or [])
        + list(skill.applicable_signals or [])
        + [skill.name, skill.description],
        lower=False,
    )[:16]


def _write_family_tree(
    *,
    family_name: str,
    family_dir: str,
    skills: Sequence[SkillSpec],
    docs_by_id: Dict[str, DocumentRecord],
    supports_by_id: Dict[str, SupportRecord],
    user_id: str,
    metadata: Dict[str, Any],
) -> Tuple[List[str], str]:
    os.makedirs(family_dir, exist_ok=True)
    child_root = family_children_visible_root(base_store_root=os.path.dirname(family_dir), family_name=family_name)
    parent_root = family_parent_visible_root(base_store_root=os.path.dirname(family_dir), family_name=family_name)
    os.makedirs(child_root, exist_ok=True)
    os.makedirs(parent_root, exist_ok=True)

    child_entries: List[Dict[str, Any]] = []
    child_paths: List[str] = []
    used_names: Dict[str, int] = {}

    ordered_skills = sorted(
        skills,
        key=lambda item: (
            normalize_text(str(item.name or ""), lower=True),
            normalize_text(str(item.description or ""), lower=True),
            str(item.skill_id or ""),
        ),
    )
    for skill in ordered_skills:
        visible_name = _unique_visible_name(_safe_visible_name(skill.name), used_names)
        relative_skill_path = os.path.join(family_name, "子技能", visible_name, "SKILL.md").replace(os.sep, "/")
        child_dir = os.path.join(child_root, visible_name)
        os.makedirs(child_dir, exist_ok=True)

        skill_supports = [
            support
            for support_id in list(skill.support_ids or [])
            for support in [supports_by_id.get(str(support_id or "").strip())]
            if support is not None
        ]
        evidence_manifest = _build_evidence_manifest(
            skill=skill,
            family_name=family_name,
            docs_by_id=docs_by_id,
            supports=skill_supports,
        )
        evidence_md = _render_evidence_md(
            skill=skill,
            family_name=family_name,
            docs_by_id=docs_by_id,
            supports=skill_supports,
        )
        child_skill = _build_child_skill_artifact(
            skill=skill,
            family_name=family_name,
            taxonomy_class=_taxonomy_class_for_skill(skill, family_name=family_name),
            metadata=metadata,
            user_id=user_id,
            evidence_manifest=evidence_manifest,
            evidence_md=evidence_md,
        )
        _write_skill_dir(child_dir, child_skill)
        child_paths.append(os.path.join(child_dir, "SKILL.md"))

        child_entries.append(
            {
                "skill_id": skill.skill_id,
                "name": skill.name,
                "description": skill.description,
                "child_type": _child_type_for_skill(skill),
                "taxonomy_class": _taxonomy_class_for_skill(skill, family_name=family_name),
                "applicable_when": skill.description or skill.objective,
                "selector_terms": _selector_terms_for_skill(skill),
                "relative_path": relative_skill_path,
            }
        )

    parent_skill = _build_parent_skill_artifact(
        family_name=family_name,
        child_entries=child_entries,
        metadata=metadata,
        user_id=user_id,
    )
    children_manifest = _build_children_manifest(
        family_name=family_name,
        child_entries=child_entries,
        parent_skill_id=parent_skill.id,
        metadata=metadata,
    )
    children_map_md = _render_children_map(family_name=family_name, child_entries=child_entries)
    parent_skill.files["references/children_manifest.json"] = json.dumps(children_manifest, ensure_ascii=False, indent=2)
    parent_skill.files["references/children_map.md"] = children_map_md
    _write_skill_dir(parent_root, parent_skill)
    return child_paths, os.path.join(parent_root, "SKILL.md")


def _write_family_tree_from_store(
    *,
    family_name: str,
    family_dir: str,
    store_skills: Sequence[Skill],
    registry_skills: Sequence[SkillSpec],
    docs_by_id: Dict[str, DocumentRecord],
    supports_by_id: Dict[str, SupportRecord],
    user_id: str,
    metadata: Dict[str, Any],
) -> Tuple[List[str], str]:
    """Writes one visible family tree using final store skills as the child source."""

    os.makedirs(family_dir, exist_ok=True)
    child_root = family_children_visible_root(base_store_root=os.path.dirname(family_dir), family_name=family_name)
    parent_root = family_parent_visible_root(base_store_root=os.path.dirname(family_dir), family_name=family_name)
    os.makedirs(child_root, exist_ok=True)
    os.makedirs(parent_root, exist_ok=True)

    child_entries: List[Dict[str, Any]] = []
    child_paths: List[str] = []
    used_names: Dict[str, int] = {}

    ordered_store_skills = sorted(
        [skill for skill in list(store_skills or []) if isinstance(skill, Skill)],
        key=lambda item: (
            normalize_text(str(item.name or ""), lower=True),
            normalize_text(str(item.description or ""), lower=True),
            str(item.id or ""),
        ),
    )
    for store_skill in ordered_store_skills:
        visible_name = _unique_visible_name(_safe_visible_name(store_skill.name), used_names)
        relative_skill_path = os.path.join(family_name, "子技能", visible_name, "SKILL.md").replace(os.sep, "/")
        child_dir = os.path.join(child_root, visible_name)
        os.makedirs(child_dir, exist_ok=True)

        matched_registry_skills = _match_registry_skills_for_store_skill(
            store_skill=store_skill,
            registry_skills=registry_skills,
        )
        matched_supports = _supports_for_registry_skills(
            skills=matched_registry_skills,
            supports_by_id=supports_by_id,
        )
        evidence_manifest = _build_evidence_manifest(
            skill=store_skill,
            family_name=family_name,
            docs_by_id=docs_by_id,
            supports=matched_supports,
        )
        evidence_md = _render_evidence_md(
            skill=store_skill,
            family_name=family_name,
            docs_by_id=docs_by_id,
            supports=matched_supports,
        )
        child_skill = _build_child_skill_artifact_from_store(
            store_skill=store_skill,
            family_name=family_name,
            metadata=metadata,
            user_id=user_id,
            evidence_manifest=evidence_manifest,
            evidence_md=evidence_md,
        )
        _write_skill_dir(child_dir, child_skill)
        child_paths.append(os.path.join(child_dir, "SKILL.md"))

        child_entries.append(
            {
                "skill_id": str(store_skill.id or "").strip(),
                "name": str(store_skill.name or "").strip(),
                "description": str(store_skill.description or "").strip(),
                "child_type": _child_type_for_registry_matches(matched_registry_skills),
                "taxonomy_class": _taxonomy_class_for_registry_matches(matched_registry_skills, fallback=family_name),
                "applicable_when": str(store_skill.description or "").strip(),
                "selector_terms": dedupe_strings(
                    list(store_skill.triggers or []) + list(store_skill.tags or []) + [str(store_skill.name or "").strip()],
                    lower=False,
                )[:16],
                "relative_path": relative_skill_path,
            }
        )

    parent_skill = _build_parent_skill_artifact(
        family_name=family_name,
        child_entries=child_entries,
        metadata=metadata,
        user_id=user_id,
    )
    children_manifest = _build_children_manifest(
        family_name=family_name,
        child_entries=child_entries,
        parent_skill_id=parent_skill.id,
        metadata=metadata,
    )
    children_map_md = _render_children_map(family_name=family_name, child_entries=child_entries)
    parent_skill.files["references/children_manifest.json"] = json.dumps(children_manifest, ensure_ascii=False, indent=2)
    parent_skill.files["references/children_map.md"] = children_map_md
    _write_skill_dir(parent_root, parent_skill)
    return child_paths, os.path.join(parent_root, "SKILL.md")


def _build_child_skill_artifact(
    *,
    skill: SkillSpec,
    family_name: str,
    taxonomy_class: str,
    metadata: Dict[str, Any],
    user_id: str,
    evidence_manifest: Dict[str, Any],
    evidence_md: str,
) -> Skill:
    extra_files = _coerce_file_mapping((skill.metadata or {}).get("files"))
    files = dict(extra_files)
    files["references/evidence.md"] = evidence_md
    files["references/evidence_manifest.json"] = json.dumps(evidence_manifest, ensure_ascii=False, indent=2)
    tags = dedupe_strings(
        list(skill.tags or [])
        + [family_name]
        + _metadata_tags(metadata)
        + [f"class:{taxonomy_class}", "kind:child", f"document_merge_state:{skill.status.value}", "canonical:true"],
        lower=False,
    )
    return Skill(
        id=skill.skill_id,
        user_id=user_id,
        name=skill.name,
        description=skill.description,
        instructions=str(skill.skill_body or "").strip(),
        triggers=list(skill.triggers or []),
        examples=list(skill.examples or []),
        tags=tags,
        version=str(skill.version or "0.1.0"),
        status=SkillStatus.ACTIVE,
        files=files,
        source={
            "source_type": "document_skill",
            "domain": skill.domain,
            "task_family": skill.task_family,
            "method_family": skill.method_family,
            "stage": skill.stage,
            "support_ids": list(skill.support_ids or []),
        },
        metadata=dict(skill.metadata or {}),
    )


def _build_child_skill_artifact_from_store(
    *,
    store_skill: Skill,
    family_name: str,
    metadata: Dict[str, Any],
    user_id: str,
    evidence_manifest: Dict[str, Any],
    evidence_md: str,
) -> Skill:
    """Builds one visible child artifact from a final local store skill."""

    files = {
        str(path): str(content or "")
        for path, content in dict(store_skill.files or {}).items()
        if str(path or "").strip() and str(path or "").strip() != "SKILL.md"
    }
    files["references/evidence.md"] = evidence_md
    files["references/evidence_manifest.json"] = json.dumps(evidence_manifest, ensure_ascii=False, indent=2)
    merged_metadata = {"family_name": family_name, **dict(store_skill.metadata or {}), **dict(metadata or {})}
    return Skill(
        id=str(store_skill.id or "").strip(),
        user_id=str(user_id or "").strip() or str(store_skill.user_id or "").strip() or DEFAULT_DOC_SKILL_USER_ID,
        name=str(store_skill.name or "").strip(),
        description=str(store_skill.description or "").strip(),
        instructions=str(store_skill.instructions or "").strip(),
        triggers=list(store_skill.triggers or []),
        examples=list(store_skill.examples or []),
        tags=dedupe_strings(list(store_skill.tags or []) + [family_name] + _metadata_tags(metadata), lower=False),
        version=str(store_skill.version or "0.1.0"),
        status=SkillStatus.ACTIVE,
        files=files,
        source=dict(store_skill.source or {}),
        metadata=merged_metadata,
    )


def _skill_id_name(skill: Any) -> Tuple[str, str]:
    """Returns one `(skill_id, skill_name)` pair for registry or store skill objects."""

    skill_id = str(getattr(skill, "skill_id", "") or getattr(skill, "id", "") or "").strip()
    skill_name = str(getattr(skill, "name", "") or "").strip()
    return skill_id, skill_name


def _supports_for_registry_skills(
    *,
    skills: Sequence[SkillSpec],
    supports_by_id: Dict[str, SupportRecord],
) -> List[SupportRecord]:
    """Collects deduplicated supports referenced by one list of registry skills."""

    out: List[SupportRecord] = []
    seen: set[str] = set()
    for skill in list(skills or []):
        for support_id in list(skill.support_ids or []):
            support = supports_by_id.get(str(support_id or "").strip())
            if support is None or support.support_id in seen:
                continue
            seen.add(support.support_id)
            out.append(support)
    return out


def _tokenize_for_matching(value: str) -> List[str]:
    """Builds compact ASCII/CJK tokens for fuzzy skill-name matching."""

    raw = normalize_text(str(value or ""), lower=True)
    if not raw:
        return []
    tokens: List[str] = []
    ascii_buf: List[str] = []
    cjk_buf: List[str] = []
    for ch in raw:
        if "\u4e00" <= ch <= "\u9fff":
            if ascii_buf:
                token = "".join(ascii_buf).strip()
                if token:
                    tokens.append(token)
                ascii_buf = []
            cjk_buf.append(ch)
            if len(cjk_buf) >= 2:
                tokens.append("".join(cjk_buf[-2:]))
        elif ch.isalnum():
            if cjk_buf:
                cjk_buf = []
            ascii_buf.append(ch)
        else:
            if ascii_buf:
                token = "".join(ascii_buf).strip()
                if token:
                    tokens.append(token)
                ascii_buf = []
            if cjk_buf:
                cjk_buf = []
    if ascii_buf:
        token = "".join(ascii_buf).strip()
        if token:
            tokens.append(token)
    return dedupe_strings(tokens, lower=False)


def _match_score(left: str, right: str) -> float:
    """Computes a simple lexical overlap score between two skill names."""

    left_norm = normalize_text(left, lower=True)
    right_norm = normalize_text(right, lower=True)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0
    if left_norm in right_norm or right_norm in left_norm:
        return 0.9
    left_tokens = set(_tokenize_for_matching(left_norm))
    right_tokens = set(_tokenize_for_matching(right_norm))
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = len(left_tokens & right_tokens)
    if overlap <= 0:
        return 0.0
    return overlap / max(len(left_tokens), len(right_tokens))


def _match_registry_skills_for_store_skill(
    *,
    store_skill: Skill,
    registry_skills: Sequence[SkillSpec],
) -> List[SkillSpec]:
    """Matches one final store skill back to one or more registry skills for evidence stitching."""

    source_map = dict(store_skill.source or {})
    skill_spec_id = str(source_map.get("skill_spec_id") or "").strip()
    if skill_spec_id:
        exact = [skill for skill in list(registry_skills or []) if str(skill.skill_id or "").strip() == skill_spec_id]
        if exact:
            return exact

    source_support_ids = {
        str(support_id or "").strip()
        for support_id in list(source_map.get("support_ids") or [])
        if str(support_id or "").strip()
    }
    if source_support_ids:
        matched = [
            skill
            for skill in list(registry_skills or [])
            if source_support_ids & {str(support_id or "").strip() for support_id in list(skill.support_ids or []) if str(support_id or "").strip()}
        ]
        if matched:
            return matched

    scored: List[Tuple[float, SkillSpec]] = []
    store_name = str(store_skill.name or "").strip()
    for registry_skill in list(registry_skills or []):
        score = max(
            _match_score(store_name, str(registry_skill.name or "").strip()),
            _match_score(str(store_skill.description or "").strip(), str(registry_skill.description or "").strip()),
        )
        if score <= 0.0:
            continue
        scored.append((score, registry_skill))
    scored.sort(key=lambda item: (-item[0], normalize_text(str(item[1].name or ""), lower=True)))
    if not scored:
        return []
    strong = [skill for score, skill in scored if score >= 0.5]
    if strong:
        return strong
    return [scored[0][1]]


def _child_type_for_registry_matches(skills: Sequence[SkillSpec]) -> str:
    """Returns the dominant child type from a set of matched registry skills."""

    for skill in list(skills or []):
        child_type = _child_type_for_skill(skill)
        if child_type:
            return child_type
    return ""


def _taxonomy_class_for_registry_matches(skills: Sequence[SkillSpec], *, fallback: str) -> str:
    """Returns the dominant taxonomy class from matched registry skills."""

    for skill in list(skills or []):
        raw = str((skill.metadata or {}).get("taxonomy_class") or "").strip()
        if raw:
            return raw
    return str(fallback or "").strip()


def _build_parent_skill_artifact(
    *,
    family_name: str,
    child_entries: Sequence[Dict[str, Any]],
    metadata: Dict[str, Any],
    user_id: str,
) -> Skill:
    description = f"{family_name} 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。"
    parent_skill_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"autoskill4doc-parent:{family_name}"))
    lines: List[str] = [
        "## 适用场景",
        f"- 当当前问题明确属于或需要路由到 {family_name} 时，先使用本总技能决定子技能选择顺序。",
        "- 本技能用于导航与组合，不替代子技能中的具体执行 SOP。",
        "",
        "## 不适用/风险边界",
        "- 不要把本技能当作具体干预脚本；真正执行时必须继续调用对应子技能。",
        "- 如存在明显高风险或危机信号，应优先调用风险/危机类子技能。",
        "",
        "## 总流程",
        "1. 先判断当前问题是否适合进入该家族或领域的处理路径。",
        "2. 再根据任务类型、阶段和风险边界选择最合适的子技能。",
        "3. 调用对应子技能执行具体步骤、规则和输出格式。",
        "4. 最后输出所选子技能、选择理由、执行顺序与风险提示。",
        "",
        "## 子技能目录",
    ]
    for item in child_entries:
        name = str(item.get("name") or "").strip()
        child_type = str(item.get("child_type") or "").strip()
        applicable = str(item.get("applicable_when") or "").strip()
        detail = applicable or str(item.get("description") or "").strip()
        if child_type:
            lines.append(f"- {name} ｜ 类型：{child_type} ｜ 适用条件：{detail}")
        else:
            lines.append(f"- {name} ｜ 适用条件：{detail}")
    lines.extend(["", "## 选用规则"])
    for item in child_entries[:12]:
        name = str(item.get("name") or "").strip()
        selector_terms = [str(term).strip() for term in list(item.get("selector_terms") or []) if str(term).strip()]
        if not name or not selector_terms:
            continue
        terms = "、".join(selector_terms[:4])
        lines.append(f"- 当问题命中“{terms}”这类线索时，优先选择 {name}。")
    lines.extend(
        [
            "",
            "## 输出格式",
            "- family_route:",
            f"  - family: {family_name}",
            "  - selected_children: [子技能名称列表]",
            "  - rationale: 说明为什么选择这些子技能",
            "  - cautions: 风险边界与切换条件",
        ]
    )
    tags = dedupe_strings(
        [family_name, "总导航", "子技能地图", "kind:parent"] + _metadata_tags(metadata),
        lower=False,
    )
    triggers = dedupe_strings(
        [family_name, f"{family_name} 总导航", f"{family_name} 子技能地图"],
        lower=False,
    )
    return Skill(
        id=parent_skill_id,
        user_id=user_id,
        name=family_name,
        description=description,
        instructions="\n".join(lines).strip(),
        triggers=triggers,
        tags=tags,
        version="0.1.0",
        status=SkillStatus.ACTIVE,
        files={},
        source={"source_type": "document_parent_skill"},
        metadata={"family_name": family_name, **dict(metadata or {})},
    )


def _build_children_manifest(
    *,
    family_name: str,
    child_entries: Sequence[Dict[str, Any]],
    parent_skill_id: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "schema": "autoskill.document.children_manifest.v2",
        "generated_at": now_iso(),
        "family_name": family_name,
        "profile_id": str(metadata.get("profile_id") or "").strip(),
        "taxonomy_axis": str(metadata.get("taxonomy_axis") or "").strip(),
        "parent_skill_id": parent_skill_id,
        "children": list(child_entries or []),
    }


def _build_evidence_manifest(
    *,
    skill: Any,
    family_name: str,
    docs_by_id: Dict[str, DocumentRecord],
    supports: Sequence[SupportRecord],
) -> Dict[str, Any]:
    skill_id, skill_name = _skill_id_name(skill)
    evidence_items: List[Dict[str, Any]] = []
    for support in supports or []:
        document = docs_by_id.get(str(support.doc_id or "").strip())
        evidence_items.append(
            {
                "support_id": support.support_id,
                "doc_id": support.doc_id,
                "document_title": str(document.title if document is not None else ""),
                "source_file": str(support.source_file or ""),
                "section": str(support.section or ""),
                "span": support.span.to_dict(),
                "relation_type": support.relation_type.value,
                "confidence": float(support.confidence or 0.0),
                "quote": str(support.excerpt or ""),
                "metadata": dict(support.metadata or {}),
            }
        )
    return {
        "schema": "autoskill.document.evidence_manifest.v1",
        "generated_at": now_iso(),
        "family_name": family_name,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "support_count": len(evidence_items),
        "supports": evidence_items,
    }


def _render_evidence_md(
    *,
    skill: Any,
    family_name: str,
    docs_by_id: Dict[str, DocumentRecord],
    supports: Sequence[SupportRecord],
) -> str:
    skill_id, skill_name = _skill_id_name(skill)
    lines: List[str] = [
        f"# {skill_name} Evidence",
        "",
        f"- family: {family_name}",
        f"- skill_id: {skill_id}",
        f"- support_count: {len(list(supports or []))}",
        "",
    ]
    if not supports:
        lines.extend(["暂无证据摘录。", ""])
        return "\n".join(lines).strip() + "\n"
    for idx, support in enumerate(supports, start=1):
        document = docs_by_id.get(str(support.doc_id or "").strip())
        title = str(document.title if document is not None else support.doc_id)
        lines.extend(
            [
                f"## Evidence {idx}",
                "",
                f"- support_id: {support.support_id}",
                f"- relation_type: {support.relation_type.value}",
                f"- document: {title}",
                f"- doc_id: {support.doc_id}",
                f"- source_file: {str(support.source_file or '')}",
                f"- section: {str(support.section or '')}",
                f"- span: {int(support.span.start)}:{int(support.span.end)}",
                f"- confidence: {float(support.confidence or 0.0):.2f}",
                f"- quote: {str(support.excerpt or '').strip()}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _render_children_map(*, family_name: str, child_entries: Sequence[Dict[str, Any]]) -> str:
    lines = [f"# {family_name} 子技能地图", "", f"- parent: `{family_name}/总技能/SKILL.md`", "", "## 子技能列表", ""]
    for idx, item in enumerate(child_entries, start=1):
        name = str(item.get("name") or "").strip()
        child_type = str(item.get("child_type") or "").strip()
        relative_path = str(item.get("relative_path") or "").strip()
        applicable = str(item.get("applicable_when") or "").strip()
        lines.append(f"{idx}. [{name}]({relative_path})")
        if child_type:
            lines.append(f"   - 类型：{child_type}")
        if applicable:
            lines.append(f"   - 适用条件：{applicable}")
    lines.append("")
    return "\n".join(lines)


def _scan_library_manifest(store_root: str) -> Dict[str, Any]:
    families: List[Dict[str, Any]] = []
    if os.path.isdir(store_root):
        for name in sorted(os.listdir(store_root)):
            if not name or name.startswith(".") or name in _ROOT_SKIP_DIRS:
                continue
            family_dir = os.path.join(store_root, name)
            if not os.path.isdir(family_dir):
                continue
            family_entry = _scan_family_entry(store_root=store_root, family_name=name)
            if family_entry is not None:
                families.append(family_entry)
    profiles_map: Dict[str, Dict[str, Any]] = {}
    for family in families:
        profile_id = str(family.get("profile_id") or "").strip()
        if not profile_id:
            continue
        profile = profiles_map.setdefault(
            profile_id,
            {
                "profile_id": profile_id,
                "taxonomy_axis": str(family.get("taxonomy_axis") or "").strip(),
                "families": [],
                "active_family_name": None,
            },
        )
        profile["taxonomy_axis"] = str(family.get("taxonomy_axis") or "").strip()
        profile["families"].append(dict(family))
        if not profile.get("active_family_name"):
            profile["active_family_name"] = str(family.get("family_name") or family.get("school_name") or "").strip() or None
    profiles = sorted(profiles_map.values(), key=lambda item: str(item.get("profile_id") or "").lower())
    return {
        "schema": "autoskill.document.library_manifest.v1",
        "generated_at": now_iso(),
        "store_root": store_root,
        "active_profile_id": str(profiles[0].get("profile_id") or "").strip() if profiles else None,
        "active_family_name": str(families[0].get("family_name") or "").strip() if families else None,
        "profiles": profiles,
        "families": families,
    }


def _scan_family_entry(*, store_root: str, family_name: str) -> Optional[Dict[str, Any]]:
    family_dir = os.path.join(store_root, family_name)
    parent_relative_path = ""
    parent_skill_path = os.path.join(family_dir, "总技能", "SKILL.md")
    if os.path.isfile(parent_skill_path):
        parent_relative_path = os.path.relpath(parent_skill_path, store_root).replace(os.sep, "/")

    children_manifest_path = os.path.join(family_dir, "总技能", "references", "children_manifest.json")
    children: List[Dict[str, Any]] = []
    profile_id = ""
    taxonomy_axis = ""
    if os.path.isfile(children_manifest_path):
        try:
            with open(children_manifest_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            profile_id = str(payload.get("profile_id") or "").strip()
            taxonomy_axis = str(payload.get("taxonomy_axis") or "").strip()
            raw_children = payload.get("children")
            if isinstance(raw_children, list):
                children = [dict(item) for item in raw_children if isinstance(item, dict)]
        except Exception:
            children = []
    if not children:
        child_root = os.path.join(family_dir, "子技能")
        if os.path.isdir(child_root):
            for name in sorted(os.listdir(child_root)):
                md_path = os.path.join(child_root, name, "SKILL.md")
                if os.path.isfile(md_path):
                    children.append(
                        {
                            "name": name,
                            "relative_path": os.path.relpath(md_path, store_root).replace(os.sep, "/"),
                        }
                    )

    if not parent_relative_path and not children:
        return None
    return {
        "family_name": family_name,
        "relative_root": family_name,
        "profile_id": profile_id,
        "taxonomy_axis": taxonomy_axis,
        "parent_relative_path": parent_relative_path,
        "child_count": len(children),
        "children": children,
    }


def _render_library_readme(manifest: Dict[str, Any]) -> str:
    families = list(manifest.get("families") or [])
    lines = [
        "# DocSkill",
        "",
        "该目录保存 AutoSkill4Doc 生成的可见技能树。",
        "",
        "## 结构",
        "",
        "- `<family_name>/总技能/SKILL.md`：总导航技能",
        "- `<family_name>/子技能/<名称>/SKILL.md`：子技能",
        "- `.runtime/document_registry/`：离线文档 registry",
        "- `.runtime/library_manifest.json`：可见技能树索引",
        "",
        "## 生成逻辑",
        "",
        "1. 文档先经过 ingest / extract / compile / register_versions。",
        "2. register_versions 持久化 registry 后，再把当前有效 skill 同步成可见父子树。",
        "3. 子技能目录来自当前有效 SkillSpec；`references/evidence.*` 来自对应 SupportRecord 和 DocumentRecord。",
        "4. 总技能不是再次抽取出来的独立文档，而是根据同一家族下当前所有子技能自动合成的导航技能。",
        "5. `children_manifest.json` 提供机器可读索引，`children_map.md` 提供人读目录。",
        "",
        "## 使用建议",
        "",
        "- 为了稳定得到期望目录名，建议在构建时显式传 `--family-name`。",
        "- 如需保留 profile / taxonomy 信息，建议同时传 `--profile-id` 和 `--taxonomy-axis`。",
        "- 已导出的 `总技能/`、`子技能/`、`references/` 不应该再作为源文档回灌；ingest 会自动跳过这些生成产物。",
        "",
        "## 已同步家族",
        "",
    ]
    if not families:
        lines.append("- 暂无已同步家族")
        lines.append("")
        return "\n".join(lines)
    for item in families:
        family_name = str(item.get("family_name") or item.get("school_name") or "").strip()
        parent_relative_path = str(item.get("parent_relative_path") or "").strip()
        child_count = int(item.get("child_count") or 0)
        if parent_relative_path:
            lines.append(f"- [{family_name}]({parent_relative_path}) ({child_count} 子技能)")
        else:
            lines.append(f"- {family_name} ({child_count} 子技能)")
    lines.append("")
    return "\n".join(lines)


def _metadata_tags(metadata: Dict[str, Any]) -> List[str]:
    tags: List[str] = []
    profile_id = str(metadata.get("profile_id") or "").strip()
    taxonomy_axis = str(metadata.get("taxonomy_axis") or "").strip()
    if profile_id:
        tags.append(f"profile:{profile_id}")
    if taxonomy_axis:
        tags.append(f"axis:{taxonomy_axis}")
    return tags


def _coerce_file_mapping(raw: Any) -> Dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    files: Dict[str, str] = {}
    for path, content in raw.items():
        rel_path = _safe_rel_file_path(str(path or "").strip())
        if not rel_path or rel_path == "SKILL.md":
            continue
        files[rel_path] = str(content or "")
    return files


def _write_skill_dir(dir_path: str, skill: Skill) -> None:
    os.makedirs(dir_path, exist_ok=True)
    files = dict(skill.files or {})
    skill_md = render_skill_md(skill)
    _write_text(os.path.join(dir_path, "SKILL.md"), skill_md)
    for rel_path, content in files.items():
        safe_rel_path = _safe_rel_file_path(rel_path)
        if not safe_rel_path or safe_rel_path == "SKILL.md":
            continue
        _write_text(os.path.join(dir_path, safe_rel_path), str(content or ""))


def _safe_visible_name(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "未命名技能"
    sanitized = safe_visible_name(raw)
    return sanitized or "未命名技能"


def _unique_visible_name(name: str, used_names: Dict[str, int]) -> str:
    base = _safe_visible_name(name)
    count = int(used_names.get(base, 0)) + 1
    used_names[base] = count
    if count == 1:
        return base
    return f"{base}-{count}"


def _safe_rel_file_path(path: str) -> str:
    raw = str(path or "").strip().replace("\\", "/")
    if not raw:
        return ""
    parts: List[str] = []
    for part in raw.split("/"):
        piece = _safe_visible_name(part)
        if not piece or piece in {".", ".."}:
            continue
        parts.append(piece)
    return "/".join(parts)


def _write_json(path: str, payload: Dict[str, Any]) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict(payload or {}), f, ensure_ascii=False, indent=2, sort_keys=False)
    return path


def _write_text(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(content or ""))
    return path
