"""
Standalone configuration helpers for AutoSkill4Doc.

This module deliberately avoids depending on `autoskill.offline` so the
document pipeline can run as an independent subsystem with its own defaults.
"""

from __future__ import annotations

import os

DEFAULT_EXTRACT_STRATEGY = "recommended"
SUPPORTED_EXTRACT_STRATEGIES = ("recommended", "strict", "chunk")
DEFAULT_DOC_SKILL_USER_ID = "u1"


def repo_root() -> str:
    """Returns the repository root inferred from this package location."""

    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(here, os.pardir, os.pardir))


def default_store_path() -> str:
    """
    Returns the default AutoSkill4Doc library root.

    Layout target:
    - <repo_root>/SkillBank/DocSkill
    """

    return os.path.join(repo_root(), "SkillBank", "DocSkill")


def default_runtime_root(store_path: str = "") -> str:
    """Returns the hidden runtime root under one AutoSkill4Doc library."""

    root = os.path.abspath(os.path.expanduser(str(store_path or "").strip() or default_store_path()))
    return os.path.join(root, ".runtime")


def default_registry_root(store_path: str = "") -> str:
    """Returns the default registry root under the AutoSkill4Doc runtime tree."""

    return os.path.join(default_runtime_root(store_path), "document_registry")


def normalize_extract_strategy(value: str) -> str:
    """Validates and normalizes the public extract strategy value."""

    raw = str(value or "").strip().lower() or DEFAULT_EXTRACT_STRATEGY
    if raw not in SUPPORTED_EXTRACT_STRATEGIES:
        raise ValueError(f"unsupported extract strategy: {value}")
    return raw
