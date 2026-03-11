"""
Legacy compatibility shim.

The document pipeline is now skill-first and no longer uses a standalone
capability induction stage by default. Keep this module small and explicit so
callers get a clear message instead of import-time breakage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol

from .common import StageLogger


@dataclass
class CapabilityInductionResult:
    """Compatibility placeholder returned by the retired inducer stage."""

    capabilities: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    inducer_name: str = "retired"


class CapabilityInducer(Protocol):
    """Compatibility placeholder for the retired capability inducer interface."""

    def induce(self, *, logger: StageLogger, **_: Any) -> CapabilityInductionResult:
        """Runs the retired capability induction stage."""


def build_capability_inducer(kind: str = "heuristic") -> CapabilityInducer:
    """Explains that capability induction is no longer the default path."""

    raise NotImplementedError(
        "offline/document no longer uses a standalone capability induction stage; "
        "use extract_skills() + compile_skills() instead"
    )


def induce_capabilities(*, logger: StageLogger = None, **_: Any) -> CapabilityInductionResult:
    """Compatibility wrapper returning an explicit retired-stage error payload."""

    _ = logger
    return CapabilityInductionResult(
        errors=[
            {
                "stage": "induce_capabilities",
                "error": "retired: use extract_skills() + compile_skills() in the skill-first document pipeline",
            }
        ]
    )
