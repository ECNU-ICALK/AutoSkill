from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLUGIN_DIR = _REPO_ROOT / "AutoSkill4OpenClaw"
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from autoskill.models import Skill  # noqa: E402
from openclaw_skill_mirror import (  # noqa: E402
    OpenClawSkillInstallConfig,
    OpenClawSkillMirror,
)


class _FakeSDK:
    def __init__(self, skills_by_user: Dict[str, List[Skill]]) -> None:
        self.skills_by_user = skills_by_user
        self.skills_by_id: Dict[str, Skill] = {}
        for bucket in skills_by_user.values():
            for skill in bucket:
                self.skills_by_id[skill.id] = skill

    def list(self, *, user_id: str) -> List[Skill]:
        return list(self.skills_by_user.get(user_id, []))

    def export_skill_dir(self, skill_id: str) -> Dict[str, str]:
        skill = self.skills_by_id[skill_id]
        return dict(skill.files or {})


def _skill(*, skill_id: str, user_id: str, name: str, prompt: str) -> Skill:
    return Skill(
        id=skill_id,
        user_id=user_id,
        name=name,
        description=f"{name} description",
        instructions=prompt,
        version="0.1.0",
        files={
            "SKILL.md": (
                "---\n"
                f"id: \"{skill_id}\"\n"
                f"name: \"{name}\"\n"
                "description: \"test\"\n"
                "version: \"0.1.0\"\n"
                "---\n\n"
                f"# {name}\n\n{prompt}\n"
            )
        },
    )


class OpenClawSkillMirrorTest(unittest.TestCase):
    def test_store_only_mode_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdk = _FakeSDK({"u1": [_skill(skill_id="s1", user_id="u1", name="Release", prompt="do it")]})
            mirror = OpenClawSkillMirror(
                config=OpenClawSkillInstallConfig(
                    mode="store_only",
                    skills_dir=tmp,
                ).normalize()
            )
            result = mirror.sync_user_skills(sdk=sdk, user_id="u1", reason="test")
            self.assertTrue(result.skipped)
            self.assertEqual(result.reason, "install_mode_disabled")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_sync_writes_skill_folders_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdk = _FakeSDK(
                {
                    "u1": [
                        _skill(skill_id="s1", user_id="u1", name="Release Checklist", prompt="check release"),
                        _skill(skill_id="s2", user_id="u1", name="Report Style", prompt="write short"),
                    ]
                }
            )
            mirror = OpenClawSkillMirror(
                config=OpenClawSkillInstallConfig(
                    mode="openclaw_mirror",
                    skills_dir=tmp,
                ).normalize()
            )
            result = mirror.sync_user_skills(sdk=sdk, user_id="u1", reason="test_sync")
            self.assertFalse(result.skipped)
            self.assertEqual(result.synced_count, 2)
            self.assertEqual(result.removed_count, 0)

            root = Path(tmp)
            manifest = json.loads((root / ".autoskill-openclaw-skill-mirror.json").read_text(encoding="utf-8"))
            skills = manifest["users"]["u1"]["skills"]
            self.assertEqual(set(skills.keys()), {"s1", "s2"})
            for item in skills.values():
                folder = root / item["folder"]
                self.assertTrue((folder / "SKILL.md").exists())
                self.assertTrue((folder / ".autoskill-managed.json").exists())

    def test_sync_prunes_removed_managed_skills_but_keeps_unknown_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill1 = _skill(skill_id="s1", user_id="u1", name="Release Checklist", prompt="check release")
            skill2 = _skill(skill_id="s2", user_id="u1", name="Report Style", prompt="write short")
            sdk = _FakeSDK({"u1": [skill1, skill2]})
            mirror = OpenClawSkillMirror(
                config=OpenClawSkillInstallConfig(
                    mode="openclaw_mirror",
                    skills_dir=tmp,
                ).normalize()
            )
            first = mirror.sync_user_skills(sdk=sdk, user_id="u1", reason="initial")
            self.assertEqual(first.synced_count, 2)

            manual_dir = Path(tmp) / "manual-skill"
            manual_dir.mkdir(parents=True, exist_ok=True)
            (manual_dir / "SKILL.md").write_text("# Manual\n", encoding="utf-8")

            sdk.skills_by_user["u1"] = [skill2]
            second = mirror.sync_user_skills(sdk=sdk, user_id="u1", reason="after_merge")
            self.assertEqual(second.synced_count, 1)
            self.assertEqual(second.removed_count, 1)
            self.assertTrue(manual_dir.exists())

            manifest = json.loads((Path(tmp) / ".autoskill-openclaw-skill-mirror.json").read_text(encoding="utf-8"))
            skills = manifest["users"]["u1"]["skills"]
            self.assertEqual(set(skills.keys()), {"s2"})

    def test_install_user_filter_skips_other_users(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdk = _FakeSDK({"u2": [_skill(skill_id="s1", user_id="u2", name="Other User", prompt="ignore")]})
            mirror = OpenClawSkillMirror(
                config=OpenClawSkillInstallConfig(
                    mode="openclaw_mirror",
                    skills_dir=tmp,
                    install_user_id="u1",
                ).normalize()
            )
            result = mirror.sync_user_skills(sdk=sdk, user_id="u2", reason="other_user")
            self.assertTrue(result.skipped)
            self.assertEqual(result.reason, "user_not_selected_for_install")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_resync_updates_skill_content_without_changing_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = _skill(skill_id="s1", user_id="u1", name="Release Checklist", prompt="version one")
            sdk = _FakeSDK({"u1": [skill]})
            mirror = OpenClawSkillMirror(
                config=OpenClawSkillInstallConfig(
                    mode="openclaw_mirror",
                    skills_dir=tmp,
                ).normalize()
            )
            first = mirror.sync_user_skills(sdk=sdk, user_id="u1", reason="v1")
            self.assertEqual(first.synced_count, 1)
            folder = Path(first.folders[0])
            self.assertIn("version one", (folder / "SKILL.md").read_text(encoding="utf-8"))

            updated_skill = _skill(skill_id="s1", user_id="u1", name="Release Checklist", prompt="version two")
            sdk.skills_by_user["u1"] = [updated_skill]
            sdk.skills_by_id["s1"] = updated_skill
            second = mirror.sync_user_skills(sdk=sdk, user_id="u1", reason="v2")
            self.assertEqual(second.synced_count, 1)
            self.assertEqual(Path(second.folders[0]), folder)
            self.assertIn("version two", (folder / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
