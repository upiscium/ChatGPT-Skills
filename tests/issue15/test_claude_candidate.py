"""Offline qualification for the isolated Arca DevSkills Claude candidate."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "packaging/build_claude_candidate.py"
SPEC = importlib.util.spec_from_file_location("arca_claude_candidate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class ClaudeCandidateTests(unittest.TestCase):
    def test_plugin_name_is_distinct_from_existing_arca(self) -> None:
        files, manifest = builder.candidate_files()
        self.assertEqual(manifest["name"], "arca-devskills")
        self.assertEqual(manifest["displayName"], "Arca DevSkills")
        self.assertNotEqual(manifest["name"], "arca-development")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("hooks", manifest)
        self.assertNotIn("commands", manifest)
        self.assertEqual(json.loads(files[".claude-plugin/plugin.json"]), manifest)

    def test_reject_unreviewed_manifest_capability(self) -> None:
        from unittest.mock import patch

        original = builder._text

        def changed(path: Path) -> str:
            if path == builder.MANIFEST:
                candidate = json.loads(original(path))
                candidate["hooks"] = {"PreToolUse": ["not-authorized"]}
                return json.dumps(candidate)
            return original(path)

        with (
            patch.object(builder, "_text", changed),
            self.assertRaisesRegex(ValueError, "Unexpected Claude manifest capability"),
        ):
            builder.candidate_files()

    def test_six_curated_skills_only(self) -> None:
        files, _ = builder.candidate_files()
        actual = sorted(
            p.split("/")[1]
            for p in files
            if p.startswith("skills/") and p.endswith("/SKILL.md")
        )
        self.assertEqual(actual, sorted(builder.SKILLS))
        self.assertNotIn("skills/dev-loop/SKILL.md", files)
        self.assertNotIn("skills/opencode-bridge/SKILL.md", files)
        self.assertNotIn("skills/pr-merge/SKILL.md", files)
        self.assertFalse(any(p.endswith((".yaml", ".svg")) for p in files))

    def test_skill_refs_are_explicitly_adapted(self) -> None:
        files, _ = builder.candidate_files()
        blueprint = files["skills/blueprint/SKILL.md"].decode()
        self.assertIn("/arca-devskills:human-review", blueprint)
        self.assertIn("/arca-devskills:issue-filer", blueprint)
        self.assertIn("[unbundled legacy skill: patch-plan]", blueprint)
        self.assertNotIn("@human-review", blueprint)
        for name in builder.SKILLS:
            data = files["skills/" + name + "/SKILL.md"].decode()
            self.assertTrue(data.startswith("---\nname: " + name + "\n"))
            self.assertIn("GitHub writes and KAGARI dispatch require", data)
            self.assertNotIn("--dangerously-skip-permissions", data)

    def test_packaged_markdown_links_are_closed(self) -> None:
        files, _ = builder.candidate_files()
        for name, payload in files.items():
            if not name.startswith("skills/") or not name.endswith(".md"):
                continue
            for link in builder.LOCAL_REFERENCE.findall(payload.decode("utf-8")):
                referenced = (Path(name).parent / link).as_posix()
                self.assertIn(referenced, files, msg=name + " -> " + link)

    def test_source_legacy_packager_is_unchanged(self) -> None:
        for path in (
            "packaging/build_candidate.py",
            "packaging/arca-development/plugin.json",
            "packaging/arca-development/.codex-plugin/plugin.json",
        ):
            committed = subprocess.check_output(
                ["git", "-C", str(ROOT), "show", "HEAD:" + path]
            )
            self.assertEqual((ROOT / path).read_bytes(), committed)

    def test_reject_unknown_skill_reference(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unreviewed skill dependency"):
            builder._adapt("Use @an-unreviewed-namespace before filing.")
        self.assertIn(
            "[unbundled legacy skill: repo-review]", builder._adapt("@repo-review")
        )

    def test_reject_unsafe_reference_link(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsafe skill-local link"):
            builder._validate_local_links(
                "[x](references/../secrets)", Path("skills/blueprint")
            )

    def test_reject_symlink_source(self) -> None:
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "source.md"
            link.symlink_to(ROOT / "skills/blueprint/SKILL.md")
            with (
                patch.object(builder, "ROOT", Path(tmp)),
                self.assertRaisesRegex(ValueError, "Symlink in candidate source"),
            ):
                builder._text(Path("source.md"))

    def test_build_is_reproducible_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "first.zip", Path(tmp) / "second.zip"
            first = builder.build(a, preview_uncommitted=True)
            second = builder.build(b, preview_uncommitted=True)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(first["sha256"], second["sha256"])
            self.assertTrue(first["preview_uncommitted"])
            self.assertFalse(first["installed_plugin_modified"])
            self.assertEqual(len(first["skills"]), 6)
            with zipfile.ZipFile(a) as archive:
                self.assertEqual(archive.namelist(), sorted(archive.namelist()))
                self.assertTrue(archive.testzip() is None)
                self.assertEqual(len(archive.namelist()), first["files"])
                for info in archive.infolist():
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual((info.external_attr >> 16) & 0o777, 0o644)
            with self.assertRaises(FileExistsError):
                builder.build(a, preview_uncommitted=True)
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_release_mode_accepts_clean_committed_inputs(self) -> None:
        """Keep the release path testable after the four files are committed."""
        from unittest.mock import patch

        original_git = builder._git
        committed_skill = Path("skills/blueprint/SKILL.md")

        def clean_index(*args: str) -> str:
            return "" if args == ("status", "--porcelain") else original_git(*args)

        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(builder, "_git", clean_index),
            patch.object(builder, "_input_sources", return_value=(committed_skill,)),
        ):
            target = Path(tmp) / "release.zip"
            receipt = builder.build(target)
            self.assertFalse(receipt["preview_uncommitted"])
            self.assertTrue(target.is_file())
            with zipfile.ZipFile(target) as archive:
                self.assertIsNone(archive.testzip())

    def test_release_mode_rejects_uncommitted_changes(self) -> None:
        """Simulate dirty status; do not depend on the checkout being dirty."""
        from unittest.mock import patch

        original = builder._git

        def dirty_index(*args: str) -> str:
            return (
                "?? scratch.txt"
                if args == ("status", "--porcelain")
                else original(*args)
            )

        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(builder, "_git", dirty_index),
        ):
            with self.assertRaisesRegex(ValueError, "Dirty checkout"):
                builder.build(Path(tmp) / "no-release.zip")
            self.assertFalse((Path(tmp) / "no-release.zip").exists())

    def test_committed_source_rejects_hidden_byte_drift(self) -> None:
        """An index marked assume-unchanged must not silently change shipped Skills."""
        from unittest.mock import patch

        source = Path("skills/blueprint/SKILL.md")
        head = builder._git("rev-parse", "HEAD")
        self.assertIsNone(builder._verify_committed_source(source, head=head))
        with self.assertRaisesRegex(ValueError, "differs from HEAD"):
            builder._verify_committed_source(source, head="0" * 40)
        original = builder._source_bytes

        def altered(path: Path) -> bytes:
            data = original(path)
            return data + b"\nHIDDEN_MUTATION\n" if path == source else data

        with (
            patch.object(builder, "_source_bytes", altered),
            self.assertRaisesRegex(ValueError, "differs from HEAD"),
        ):
            builder._verify_committed_source(source)

    def test_committed_source_verifies_raw_bytes_not_normalized_crlf(self) -> None:
        """A text loader must not conceal CRLF changes in the physical source."""
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.md").write_bytes(b"LINE\r\n")
            git_blob = subprocess.CompletedProcess(
                args=["git"], returncode=0, stdout=b"LINE\n"
            )
            with (
                patch.object(builder, "ROOT", root),
                patch.object(builder.subprocess, "run", return_value=git_blob),
                self.assertRaisesRegex(ValueError, "differs from HEAD"),
            ):
                builder._verify_committed_source(Path("sample.md"), head="a" * 40)

    def test_release_rejects_hidden_source_edit_when_index_is_clean(
        self,
    ) -> None:
        """A clean Git status cannot hide changed bytes of a tracked Skill."""
        from unittest.mock import patch

        original_git = builder._git
        original_bytes = builder._source_bytes
        source = Path("skills/blueprint/SKILL.md")

        def lying_index(*args: str) -> str:
            return "" if args == ("status", "--porcelain") else original_git(*args)

        def hidden_edit(path: Path) -> bytes:
            data = original_bytes(path)
            return data + b"\nHIDDEN_EDIT\n" if path == source else data

        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(builder, "_git", lying_index),
            patch.object(builder, "_source_bytes", hidden_edit),
            patch.object(builder, "_input_sources", return_value=(source,)),
        ):
            target = Path(tmp) / "uncommitted.zip"
            with self.assertRaisesRegex(ValueError, "differs from HEAD"):
                builder.build(target)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
