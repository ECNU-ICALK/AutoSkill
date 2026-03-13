"""
Mirror AutoSkill-managed skills into the local OpenClaw skills directory.

The plugin keeps AutoSkill's local store as the source of truth for extraction,
maintenance, delete/merge/rollback, then exports active skill artifacts into the
OpenClaw skill folder so they are directly installable by OpenClaw.
"""

from __future__ import annotations

import json
import shutil
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from autoskill.management.artifacts import ensure_skill_files
from autoskill.management.formats.agent_skill import skill_dir_name
from autoskill.models import Skill

_DEFAULT_MANIFEST = ".autoskill-openclaw-skill-mirror.json"
_MANAGED_MARKER = ".autoskill-managed.json"


def _log(message: str) -> None:
    """Run log."""
    print(f"[openclaw-skill-mirror] {message}", flush=True)


def _safe_text(value: Any) -> str:
    """Run safe text."""
    return str(value or "").strip()


def _slug_token(value: Any, *, fallback: str, max_len: int = 48) -> str:
    """Run slug token."""
    text = _safe_text(value).lower()
    if not text:
        return fallback
    out: List[str] = []
    prev_dash = False
    for ch in text:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
            continue
        if ch in {"-", "_"}:
            if not prev_dash:
                out.append("-")
                prev_dash = True
            continue
        if ch.isspace():
            if not prev_dash:
                out.append("-")
                prev_dash = True
    slug = "".join(out).strip("-")
    if not slug:
        slug = fallback
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-") or fallback
    return slug


def detect_openclaw_skills_dir(explicit_path: str = "") -> str:
    """
    Resolve the default OpenClaw skills directory.

    The current official default is `~/.openclaw/workspace/skills`. We keep a few
    legacy-compatible fallbacks if users already have older bot skill directories.
    """

    explicit = _safe_text(explicit_path)
    if explicit:
        return str(Path(explicit).expanduser().resolve())

    home = Path.home()
    candidates = [
        home / ".openclaw" / "workspace" / "skills",
        home / ".openclaw" / "skills",
        home / ".moltbot" / "skills",
        home / ".clawbot" / "skills",
    ]
    for candidate in candidates:
        try:
            if candidate.exists():
                return str(candidate.resolve())
        except Exception:
            continue
    return str(candidates[0].resolve())


@dataclass
class OpenClawSkillInstallConfig:
    mode: str = "openclaw_mirror"
    skills_dir: str = ""
    install_user_id: str = ""
    manifest_name: str = _DEFAULT_MANIFEST
    prune: bool = True

    def normalize(self) -> "OpenClawSkillInstallConfig":
        """Run normalize."""
        mode = _safe_text(self.mode).lower()
        if mode not in {"store_only", "openclaw_mirror"}:
            mode = "openclaw_mirror"
        self.mode = mode
        self.skills_dir = detect_openclaw_skills_dir(self.skills_dir)
        self.install_user_id = _safe_text(self.install_user_id)
        manifest = _safe_text(self.manifest_name) or _DEFAULT_MANIFEST
        if "/" in manifest or "\\" in manifest:
            manifest = Path(manifest).name or _DEFAULT_MANIFEST
        self.manifest_name = manifest
        self.prune = bool(self.prune)
        return self

    @property
    def enabled(self) -> bool:
        """Run enabled."""
        return self.mode == "openclaw_mirror"


@dataclass
class OpenClawSkillMirrorResult:
    enabled: bool
    user_id: str
    skills_dir: str
    synced_count: int = 0
    removed_count: int = 0
    skipped: bool = False
    reason: str = ""
    folders: List[str] = field(default_factory=list)


class OpenClawSkillMirror:
    """Synchronize user-owned AutoSkill artifacts into OpenClaw skills folders."""

    def __init__(self, *, config: Optional[OpenClawSkillInstallConfig] = None) -> None:
        """Run init."""
        self.config = (config or OpenClawSkillInstallConfig()).normalize()
        self._lock = threading.Lock()

    def status(self) -> Dict[str, Any]:
        """Run status."""
        return {
            "mode": str(self.config.mode),
            "enabled": bool(self.config.enabled),
            "skills_dir": str(self.config.skills_dir),
            "install_user_id": str(self.config.install_user_id or ""),
            "manifest_name": str(self.config.manifest_name),
            "prune": bool(self.config.prune),
        }

    def sync_user_skills(
        self,
        *,
        sdk: Any,
        user_id: str,
        reason: str = "",
    ) -> OpenClawSkillMirrorResult:
        """Mirror one user's active skills into the target OpenClaw skills folder."""
        uid = _safe_text(user_id)
        result = OpenClawSkillMirrorResult(
            enabled=bool(self.config.enabled),
            user_id=uid,
            skills_dir=str(self.config.skills_dir),
        )
        if not self.config.enabled:
            result.skipped = True
            result.reason = "install_mode_disabled"
            return result
        if not uid:
            result.skipped = True
            result.reason = "missing_user_id"
            return result

        selected_uid = _safe_text(self.config.install_user_id)
        if selected_uid and uid != selected_uid:
            result.skipped = True
            result.reason = "user_not_selected_for_install"
            return result

        root = Path(self.config.skills_dir).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)

        with self._lock:
            manifest = self._load_manifest(root)
            users = manifest.get("users")
            if not isinstance(users, dict):
                users = {}
            current = users.get(uid)
            current_skills = current.get("skills") if isinstance(current, dict) else {}
            if not isinstance(current_skills, dict):
                current_skills = {}

            used_folders = {
                entry.name
                for entry in root.iterdir()
                if entry.is_dir()
            }
            next_skills: Dict[str, Dict[str, Any]] = {}
            active_skills = list(sdk.list(user_id=uid) or [])

            for skill in active_skills:
                skill_id = _safe_text(getattr(skill, "id", ""))
                if not skill_id:
                    continue
                prev = current_skills.get(skill_id) if isinstance(current_skills.get(skill_id), dict) else {}
                folder_name = _safe_text(prev.get("folder") if isinstance(prev, dict) else "")
                if not folder_name:
                    folder_name = self._allocate_folder_name(
                        skill=skill,
                        user_id=uid,
                        used_folders=used_folders,
                    )
                used_folders.add(folder_name)

                files = sdk.export_skill_dir(skill_id) or ensure_skill_files(skill)
                self._write_skill_dir(
                    root=root,
                    folder_name=folder_name,
                    skill=skill,
                    user_id=uid,
                    files=files,
                )
                next_skills[skill_id] = {
                    "folder": folder_name,
                    "name": _safe_text(getattr(skill, "name", "")),
                    "version": _safe_text(getattr(skill, "version", "")),
                    "updated_at": _safe_text(getattr(skill, "updated_at", "")),
                    "mirrored_at_ms": int(time.time() * 1000),
                }

            removed_count = 0
            if self.config.prune:
                stale_ids = [sid for sid in current_skills.keys() if sid not in next_skills]
                for sid in stale_ids:
                    folder_name = _safe_text(
                        (current_skills.get(sid) or {}).get("folder")
                        if isinstance(current_skills.get(sid), dict)
                        else ""
                    )
                    if folder_name and self._remove_managed_skill_dir(root=root, folder_name=folder_name):
                        removed_count += 1

            users[uid] = {
                "skills": next_skills,
                "last_reason": _safe_text(reason),
                "synced_at_ms": int(time.time() * 1000),
            }
            manifest["version"] = 1
            manifest["mode"] = str(self.config.mode)
            manifest["skills_dir"] = str(root)
            manifest["users"] = users
            self._save_manifest(root, manifest)

        result.synced_count = len(next_skills)
        result.removed_count = int(removed_count)
        result.folders = [
            str((root / str(item.get("folder") or "")).resolve())
            for item in next_skills.values()
            if isinstance(item, dict) and _safe_text(item.get("folder"))
        ]
        _log(
            f"sync completed user={uid} synced={result.synced_count} removed={result.removed_count} "
            f"skills_dir={root} reason={_safe_text(reason) or '<none>'}"
        )
        return result

    def _allocate_folder_name(
        self,
        *,
        skill: Skill,
        user_id: str,
        used_folders: set[str],
    ) -> str:
        """Run allocate folder name."""
        skill_slug = _slug_token(skill_dir_name(skill), fallback="skill", max_len=40)
        user_slug = _slug_token(user_id, fallback="user", max_len=24)
        short_id = _slug_token(str(skill.id or "")[:8], fallback="skill", max_len=12)
        base = f"autoskill-{user_slug}-{skill_slug}-{short_id}"
        candidate = base
        idx = 2
        while candidate in used_folders:
            candidate = f"{base}-{idx}"
            idx += 1
        return candidate

    def _write_skill_dir(
        self,
        *,
        root: Path,
        folder_name: str,
        skill: Skill,
        user_id: str,
        files: Dict[str, str],
    ) -> None:
        """Run write skill dir."""
        target = (root / folder_name).resolve()
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

        for rel_path, content in dict(files or {}).items():
            rel = self._safe_rel_path(rel_path)
            if not rel:
                continue
            abs_path = (target / rel).resolve()
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(str(content or ""), encoding="utf-8")

        marker = {
            "managed_by": "autoskill_openclaw_plugin",
            "skill_id": str(skill.id),
            "user_id": str(user_id),
            "name": str(skill.name or ""),
            "version": str(skill.version or ""),
            "mirrored_at_ms": int(time.time() * 1000),
        }
        (target / _MANAGED_MARKER).write_text(
            json.dumps(marker, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _remove_managed_skill_dir(self, *, root: Path, folder_name: str) -> bool:
        """Run remove managed skill dir."""
        target = (root / folder_name).resolve()
        if not target.exists() or not target.is_dir():
            return False
        shutil.rmtree(target)
        return True

    def _load_manifest(self, root: Path) -> Dict[str, Any]:
        """Run load manifest."""
        path = root / self.config.manifest_name
        if not path.exists():
            return {"version": 1, "users": {}}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {"version": 1, "users": {}}
        return data if isinstance(data, dict) else {"version": 1, "users": {}}

    def _save_manifest(self, root: Path, manifest: Dict[str, Any]) -> None:
        """Run save manifest."""
        path = root / self.config.manifest_name
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _safe_rel_path(self, rel_path: Any) -> str:
        """Run safe rel path."""
        parts: List[str] = []
        for part in str(rel_path or "").replace("\\", "/").split("/"):
            token = _safe_text(part)
            if not token or token in {".", ".."}:
                continue
            parts.append(token.replace("..", "_"))
        return "/".join(parts)
