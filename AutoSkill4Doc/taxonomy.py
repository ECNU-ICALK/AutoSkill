"""Configurable skill taxonomy loader for document extraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
import json
import os
import re
from typing import Any, Dict, List, Optional


_STABLE_BASE_TYPES = (
    "macro_protocol",
    "session_skill",
    "micro_skill",
    "safety_rule",
    "knowledge_reference",
)
_DEFAULT_BASE_TYPE = "session_skill"


def _normalize_key(value: Any) -> str:
    """Normalizes taxonomy identifiers for matching."""

    return re.sub(r"\s+", " ", str(value or "").strip()).lower()


def _coerce_str_list(value: Any) -> List[str]:
    """Normalizes arbitrary list-like values into stripped string lists."""

    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _coerce_base_type(value: Any) -> str:
    """Normalizes one internal base asset type."""

    raw = _normalize_key(value)
    return raw if raw in _STABLE_BASE_TYPES else _DEFAULT_BASE_TYPE


def _safe_profile_component(value: Any) -> str:
    """Builds a stable id-safe component from a visible taxonomy value."""

    raw = _normalize_key(value)
    raw = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", raw).strip("_")
    return raw or "default"


def _load_yaml_like(text: str, *, source: str) -> Dict[str, Any]:
    """Loads a YAML-like config using PyYAML when available, otherwise JSON."""

    try:
        import yaml  # type: ignore

        payload = yaml.safe_load(text)
    except Exception:
        payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError(f"skill taxonomy at {source} must decode into an object")
    return {str(key): value for key, value in payload.items()}


def _read_builtin_taxonomy(name: str) -> Dict[str, Any]:
    """Reads one built-in taxonomy resource."""

    resource_name = f"{str(name or '').strip()}.yaml"
    package = resources.files("AutoSkill4Doc.skill_taxonomies")
    path = package.joinpath(resource_name)
    if not path.is_file():
        raise FileNotFoundError(resource_name)
    return _load_yaml_like(path.read_text(encoding="utf-8"), source=resource_name)


def _read_taxonomy_path(path: str) -> Dict[str, Any]:
    """Reads one user-provided taxonomy file."""

    src = os.path.abspath(os.path.expanduser(str(path or "").strip()))
    with open(src, "r", encoding="utf-8") as f:
        return _load_yaml_like(f.read(), source=src)


def _merge_taxonomy_payloads(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Merges a base taxonomy with one overlay by base_type."""

    merged = dict(base or {})
    for key in ("taxonomy_id", "domain_type", "display_name", "default_base_type", "family_axis", "default_family_name"):
        value = str(overlay.get(key) or "").strip()
        if value:
            merged[key] = value

    asset_map: Dict[str, Dict[str, Any]] = {}
    for item in list(base.get("asset_types") or []):
        if isinstance(item, dict):
            normalized = _coerce_base_type(item.get("base_type"))
            asset_map[normalized] = {**item, "base_type": normalized}
    for item in list(overlay.get("asset_types") or []):
        if not isinstance(item, dict):
            continue
        normalized = _coerce_base_type(item.get("base_type"))
        asset_map[normalized] = {**asset_map.get(normalized, {}), **item, "base_type": normalized}

    ordered: List[Dict[str, Any]] = []
    seen = set()
    for base_type in _STABLE_BASE_TYPES:
        if base_type in asset_map:
            ordered.append(asset_map[base_type])
            seen.add(base_type)
    for base_type, payload in asset_map.items():
        if base_type not in seen:
            ordered.append(payload)
    merged["asset_types"] = ordered
    if "family_candidates" in base or "family_candidates" in overlay:
        merged["family_candidates"] = [item for item in list(base.get("family_candidates") or []) if isinstance(item, dict)]
        overlay_candidates = [item for item in list(overlay.get("family_candidates") or []) if isinstance(item, dict)]
        if overlay_candidates:
            merged["family_candidates"] = overlay_candidates
    return merged


@dataclass
class TaxonomyAssetType:
    """One domain-specific label mapping onto an internal stable asset type."""

    base_type: str
    label: str = ""
    description: str = ""
    aliases: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalizes taxonomy type fields."""

        self.base_type = _coerce_base_type(self.base_type)
        self.label = str(self.label or "").strip() or self.base_type
        self.description = str(self.description or "").strip()
        aliases = [self.base_type, self.label, *list(self.aliases or [])]
        deduped: List[str] = []
        seen = set()
        for alias in aliases:
            value = str(alias or "").strip()
            if not value:
                continue
            key = _normalize_key(value)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(value)
        self.aliases = deduped

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaxonomyAssetType":
        """Builds one taxonomy asset type from plain data."""

        return cls(
            base_type=str(data.get("base_type") or "").strip(),
            label=str(data.get("label") or "").strip(),
            description=str(data.get("description") or "").strip(),
            aliases=_coerce_str_list(data.get("aliases")),
        )


@dataclass
class SkillTaxonomy:
    """Loaded skill taxonomy used to guide extraction and normalize aliases."""

    taxonomy_id: str
    domain_type: str
    display_name: str = ""
    default_base_type: str = _DEFAULT_BASE_TYPE
    asset_types: List[TaxonomyAssetType] = field(default_factory=list)
    family_axis: str = ""
    default_family_name: str = ""
    family_candidates: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalizes taxonomy metadata and asset mappings."""

        self.taxonomy_id = str(self.taxonomy_id or "").strip() or "default"
        self.domain_type = str(self.domain_type or "").strip() or self.taxonomy_id
        self.display_name = str(self.display_name or "").strip() or self.taxonomy_id
        self.default_base_type = _coerce_base_type(self.default_base_type)
        self.asset_types = [
            item if isinstance(item, TaxonomyAssetType) else TaxonomyAssetType.from_dict(item)
            for item in list(self.asset_types or [])
        ]
        self.family_axis = str(self.family_axis or "").strip()
        self.default_family_name = str(self.default_family_name or "").strip()
        self.family_candidates = [
            {
                "id": str(item.get("id") or "").strip(),
                "name": str(item.get("name") or "").strip(),
                "aliases": _coerce_str_list(item.get("aliases")),
            }
            for item in list(self.family_candidates or [])
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]
        if not self.asset_types:
            self.asset_types = [TaxonomyAssetType(base_type=base_type) for base_type in _STABLE_BASE_TYPES]

    @property
    def alias_map(self) -> Dict[str, str]:
        """Builds a normalized alias -> base type map."""

        mapping: Dict[str, str] = {}
        for item in self.asset_types:
            for alias in item.aliases:
                mapping[_normalize_key(alias)] = item.base_type
        return mapping

    def normalize_asset_type(self, value: Any) -> str:
        """Maps a domain-specific label or alias to an internal stable asset type."""

        raw = _normalize_key(value)
        if not raw:
            return self.default_base_type
        return self.alias_map.get(raw, _coerce_base_type(raw))

    def prompt_guidance(self) -> str:
        """Renders concise prompt guidance for document extraction."""

        lines = [
            f"Domain type is externally provided as `{self.domain_type}`.",
            "Do not infer or output domain_type.",
            "Return asset_type using ONLY the internal base types: "
            "macro_protocol | session_skill | micro_skill | safety_rule | knowledge_reference.",
        ]
        pretty_lines: List[str] = []
        for item in self.asset_types:
            alias_text = ", ".join([alias for alias in item.aliases if _normalize_key(alias) != _normalize_key(item.base_type)])
            detail = f"- {item.label} -> {item.base_type}"
            if item.description:
                detail += f": {item.description}"
            if alias_text:
                detail += f" (aliases: {alias_text})"
            pretty_lines.append(detail)
        if pretty_lines:
            lines.append("Domain-specific labels and aliases:")
            lines.extend(pretty_lines)
        if self.family_candidates:
            lines.append("Configured family candidates:")
            for item in self.family_candidates:
                alias_text = ", ".join(list(item.get("aliases") or []))
                detail = f"- {str(item.get('name') or '').strip()}"
                if alias_text:
                    detail += f" (aliases: {alias_text})"
                lines.append(detail)
        return "\n".join(lines)

    def resolve_family_name(self, *, requested: str = "", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Resolves the visible family name with request and metadata precedence."""

        md = dict(metadata or {})
        for candidate in (
            str(requested or "").strip(),
            str(md.get("family_name") or "").strip(),
            str(md.get("school_name") or "").strip(),
            self.default_family_name,
        ):
            if candidate:
                return candidate
        return ""

    def resolve_axis_label(self, *, requested: str = "") -> str:
        """Resolves the visible axis label for manifests and tags."""

        return str(requested or "").strip() or self.family_axis

    def derive_profile_id(self, *, requested: str = "", family_name: str = "") -> str:
        """Builds a stable profile id when the caller does not provide one."""

        explicit = str(requested or "").strip()
        if explicit:
            return explicit
        family = _safe_profile_component(family_name or self.default_family_name or "default")
        taxonomy = _safe_profile_component(self.taxonomy_id or self.domain_type or "default")
        return f"{taxonomy}::{family}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the taxonomy to plain data."""

        return {
            "taxonomy_id": self.taxonomy_id,
            "domain_type": self.domain_type,
            "display_name": self.display_name,
            "default_base_type": self.default_base_type,
            "family_axis": self.family_axis,
            "default_family_name": self.default_family_name,
            "family_candidates": [
                {
                    "id": str(item.get("id") or "").strip(),
                    "name": str(item.get("name") or "").strip(),
                    "aliases": list(item.get("aliases") or []),
                }
                for item in self.family_candidates
            ],
            "asset_types": [
                {
                    "base_type": item.base_type,
                    "label": item.label,
                    "description": item.description,
                    "aliases": list(item.aliases or []),
                }
                for item in self.asset_types
            ],
        }


def list_builtin_skill_taxonomies() -> List[str]:
    """Lists built-in taxonomy ids packaged with AutoSkill4Doc."""

    package = resources.files("AutoSkill4Doc.skill_taxonomies")
    names: List[str] = []
    for item in package.iterdir():
        if item.is_file() and item.name.endswith(".yaml"):
            names.append(os.path.splitext(item.name)[0])
    return sorted(set(names))


def load_skill_taxonomy(*, domain_type: str = "", taxonomy_path: str = "") -> SkillTaxonomy:
    """Loads a default taxonomy plus optional built-in or file override."""

    base = _read_builtin_taxonomy("default")
    overlay: Dict[str, Any] = {}
    domain_key = str(domain_type or "").strip()
    path = str(taxonomy_path or "").strip()
    if path:
        overlay = _read_taxonomy_path(path)
    elif domain_key and domain_key.lower() != "default":
        try:
            overlay = _read_builtin_taxonomy(domain_key)
        except FileNotFoundError:
            overlay = {}

    merged = _merge_taxonomy_payloads(base, overlay)
    if domain_key:
        merged["domain_type"] = domain_key
        if not str(overlay.get("taxonomy_id") or "").strip():
            merged["taxonomy_id"] = domain_key
    return SkillTaxonomy(
        taxonomy_id=str(merged.get("taxonomy_id") or "default").strip() or "default",
        domain_type=str(merged.get("domain_type") or domain_key or "default").strip() or "default",
        display_name=str(merged.get("display_name") or "").strip(),
        default_base_type=str(merged.get("default_base_type") or _DEFAULT_BASE_TYPE).strip(),
        family_axis=str(merged.get("family_axis") or "").strip(),
        default_family_name=str(merged.get("default_family_name") or "").strip(),
        family_candidates=[item for item in list(merged.get("family_candidates") or []) if isinstance(item, dict)],
        asset_types=[
            TaxonomyAssetType.from_dict(item)
            for item in list(merged.get("asset_types") or [])
            if isinstance(item, dict)
        ],
    )
