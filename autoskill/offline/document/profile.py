"""
Domain profile loading for the offline document pipeline.

Profiles provide editable extraction priors such as:
- task vocabularies
- method vocabularies
- stage vocabularies

The runtime stays skill-first; profiles only guide extraction and normalization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from .common import dedupe_strings
from .models import SerializableModel

_PROFILE_PACKAGE = "autoskill.offline.document.domain_profiles"


def _coerce_str_list(raw: Any) -> List[str]:
    """Normalizes arbitrary list-like content into stripped string lists."""

    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        return [str(v).strip() for v in raw if str(v).strip()]
    s = str(raw).strip()
    return [s] if s else []


def _coerce_groups(raw: Any) -> List["KeywordGroup"]:
    """Normalizes profile keyword groups from dict/list input."""

    groups: List[KeywordGroup] = []
    if raw is None:
        return groups
    if isinstance(raw, KeywordGroup):
        return [raw]
    if isinstance(raw, dict):
        for label, aliases in raw.items():
            groups.append(KeywordGroup(label=str(label).strip(), aliases=_coerce_str_list(aliases)))
        return groups
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, KeywordGroup):
                groups.append(item)
                continue
            if isinstance(item, dict):
                groups.append(KeywordGroup.from_dict(item))
                continue
            label = str(item).strip()
            if label:
                groups.append(KeywordGroup(label=label, aliases=[label]))
    return groups


@dataclass
class KeywordGroup(SerializableModel):
    """One normalized family label plus a list of aliases/patterns."""

    label: str
    aliases: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.label = str(self.label or "").strip()
        self.aliases = dedupe_strings([self.label] + _coerce_str_list(self.aliases), lower=False)
        self.validate()

    def validate(self) -> None:
        if not self.label:
            raise ValueError("KeywordGroup.label must not be empty")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeywordGroup":
        return cls(
            label=str((data or {}).get("label") or "").strip(),
            aliases=_coerce_str_list((data or {}).get("aliases")),
        )


@dataclass
class DomainProfile(SerializableModel):
    """Editable extraction priors for one domain."""

    domain: str = "default"
    default_task_family: str = "guidance"
    task_keywords: List[KeywordGroup] = field(default_factory=list)
    method_keywords: List[KeywordGroup] = field(default_factory=list)
    stage_keywords: List[KeywordGroup] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.domain = str(self.domain or "default").strip() or "default"
        self.default_task_family = str(self.default_task_family or "guidance").strip() or "guidance"
        self.task_keywords = _coerce_groups(self.task_keywords)
        self.method_keywords = _coerce_groups(self.method_keywords)
        self.stage_keywords = _coerce_groups(self.stage_keywords)
        self.metadata = dict(self.metadata or {})
        self.validate()

    def validate(self) -> None:
        if not self.domain:
            raise ValueError("DomainProfile.domain must not be empty")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainProfile":
        payload = dict(data or {})
        return cls(
            domain=str(payload.get("domain") or "default").strip() or "default",
            default_task_family=str(payload.get("default_task_family") or "guidance").strip() or "guidance",
            task_keywords=_coerce_groups(payload.get("task_keywords")),
            method_keywords=_coerce_groups(payload.get("method_keywords")),
            stage_keywords=_coerce_groups(payload.get("stage_keywords")),
            metadata=dict(payload.get("metadata") or {}),
        )

    def family_mapping(self, field_name: str) -> List[Tuple[str, List[str]]]:
        """Returns one keyword mapping in extractor-friendly tuple form."""

        groups = list(getattr(self, field_name, []) or [])
        return [(group.label, list(group.aliases or [])) for group in groups]

    def merge(self, other: "DomainProfile") -> "DomainProfile":
        """Merges another profile into this one, preferring explicit overrides."""

        def merge_groups(left: List[KeywordGroup], right: List[KeywordGroup]) -> List[KeywordGroup]:
            merged: Dict[str, List[str]] = {}
            for group in list(left or []) + list(right or []):
                bucket = merged.setdefault(group.label, [])
                bucket.extend(list(group.aliases or []))
            return [
                KeywordGroup(label=label, aliases=dedupe_strings(aliases, lower=False))
                for label, aliases in merged.items()
            ]

        return DomainProfile(
            domain=str(other.domain or self.domain or "default").strip() or "default",
            default_task_family=str(other.default_task_family or self.default_task_family or "guidance").strip() or "guidance",
            task_keywords=merge_groups(self.task_keywords, other.task_keywords),
            method_keywords=merge_groups(self.method_keywords, other.method_keywords),
            stage_keywords=merge_groups(self.stage_keywords, other.stage_keywords),
            metadata={**dict(self.metadata or {}), **dict(other.metadata or {})},
        )


def _read_profile_json_file(path: str) -> Dict[str, Any]:
    """Reads one JSON profile from disk."""

    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise ValueError(f"domain profile must be a JSON object: {path}")
    return obj


def _read_builtin_profile(name: str) -> Optional[Dict[str, Any]]:
    """Reads one packaged built-in profile by name."""

    target = f"{str(name or '').strip().lower()}.json"
    try:
        with resources.open_text(_PROFILE_PACKAGE, target, encoding="utf-8") as f:
            obj = json.load(f)
    except FileNotFoundError:
        return None
    if not isinstance(obj, dict):
        raise ValueError(f"invalid built-in domain profile: {target}")
    return obj


def list_builtin_domain_profiles() -> List[str]:
    """Lists packaged built-in domain profile names."""

    names: List[str] = []
    for item in resources.contents(_PROFILE_PACKAGE):
        if item.endswith(".json"):
            names.append(item[:-5])
    return sorted(set(names))


def load_domain_profile(*, domain: str = "", profile_path: str = "") -> DomainProfile:
    """
    Loads a resolved domain profile.

    Resolution order:
    1. built-in `default`
    2. built-in `<domain>` when available
    3. optional user JSON file override
    """

    base_obj = _read_builtin_profile("default") or {"domain": "default"}
    profile = DomainProfile.from_dict(base_obj)

    domain_name = str(domain or "").strip().lower()
    if domain_name and domain_name != "default":
        built_in = _read_builtin_profile(domain_name)
        if built_in is not None:
            profile = profile.merge(DomainProfile.from_dict(built_in))

    override_path = str(profile_path or "").strip()
    if override_path:
        override_abs = os.path.abspath(os.path.expanduser(override_path))
        profile = profile.merge(DomainProfile.from_dict(_read_profile_json_file(override_abs)))

    return profile
