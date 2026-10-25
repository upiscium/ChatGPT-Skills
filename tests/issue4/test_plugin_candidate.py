"""Offline candidate packaging and source/Plugin contract tests (no installation)."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "packaging" / "build_candidate.py"


class PluginCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="arca-vnext-packaging-")
        cls.output = Path(cls.temp.name) / "candidate.zip"
        p = subprocess.run([sys.executable, str(BUILDER), "--out", str(cls.output)],
                           check=True, capture_output=True, text=True)
        cls.result = json.loads(p.stdout)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_uninstalled_candidate_scope(self):
        self.assertFalse(self.result["installed_plugin_modified"])
        self.assertEqual(self.result["candidate_version"], "0.2.0-rc.1")
        with zipfile.ZipFile(self.output) as archive:
            names = set(archive.namelist())
        self.assertIn("plugin.json", names)
        self.assertIn(".codex-plugin/plugin.json", names)
        self.assertEqual(sum(p.startswith("skills/") and p.endswith("/SKILL.md") for p in names), 20)
        self.assertFalse(any(p.startswith(("tests/", "docs/", "uninstalled/", "packaging/")) for p in names))

    def test_preserved_feature_contracts_are_available(self):
        with zipfile.ZipFile(self.output) as archive:
            for path in ("feature-contract.md", "scope-change-gate.md", "feature-acceptance-gate.md"):
                self.assertIn("skills/human-review/references/" + path, archive.namelist())
            feature = archive.read("skills/human-review/references/feature-contract.md").decode()
            scope = archive.read("skills/human-review/references/scope-change-gate.md").decode()
            acceptance = archive.read("skills/human-review/references/feature-acceptance-gate.md").decode()
        self.assertIn("not an execution grant", feature)
        for kind in ("A —", "B —", "C —", "D —"):
            self.assertIn(kind, scope)
        for state in ("goal-satisfied", "in-spec-defect", "specification-goal-mismatch", "unknown"):
            self.assertIn(state, acceptance)

    def test_new_defaults_and_legacy_compatibility(self):
        import yaml
        with zipfile.ZipFile(self.output) as archive:
            for name in ("dev-loop", "repo-review"):
                meta = yaml.safe_load(archive.read(f"skills/{name}/agents/openai.yaml"))
                self.assertTrue(meta["policy"]["allow_implicit_invocation"])
            for name in ("patch-plan", "opencode-bridge", "opencode-reviewer",
                         "change-review", "debug-investigate"):
                meta = yaml.safe_load(archive.read(f"skills/{name}/agents/openai.yaml"))
                self.assertFalse(meta["policy"]["allow_implicit_invocation"], name)
            reviewer = yaml.safe_load(archive.read("skills/repo-review/agents/openai.yaml"))
            self.assertNotIn("icon_small", reviewer["interface"])
            self.assertNotIn("icon_large", reviewer["interface"])

    def test_relative_markdown_and_icon_references_resolve(self):
        import posixpath
        import re
        import yaml
        with zipfile.ZipFile(self.output) as archive:
            names = set(archive.namelist())
            for path in sorted(p for p in names if p.endswith(".md")):
                for target in re.findall(r"\]\(([^)]+)\)", archive.read(path).decode()):
                    if target.startswith(("https:", "http:", "#", "mailto:")):
                        continue
                    target = target.split("#")[0]
                    if not target:
                        continue
                    dest = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
                    self.assertIn(dest, names, (path, target))
            for path in sorted(p for p in names if p.endswith("/agents/openai.yaml")):
                meta = yaml.safe_load(archive.read(path))
                for icon in ("icon_small", "icon_large"):
                    if icon in meta.get("interface", {}):
                        dest = posixpath.normpath(posixpath.join(posixpath.dirname(posixpath.dirname(path)), meta["interface"][icon]))
                        self.assertIn(dest, names, (path, icon))

    def test_untracked_local_skill_files_are_not_packaged(self):
        import os
        directory = ROOT / "skills" / "blueprint" / "references"
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=directory,
            prefix=".arca-vnext-untracked-", suffix=".md", delete=False
        ) as fixture:
            fixture.write("not part of the committed source\n")
            probe = Path(fixture.name)
        try:
            result = Path(self.temp.name) / "ignore-local.zip"
            subprocess.run(
                [sys.executable, str(BUILDER), "--out", str(result)],
                check=True, capture_output=True
            )
            with zipfile.ZipFile(result) as archive:
                self.assertNotIn(probe.relative_to(ROOT).as_posix(), archive.namelist())
                self.assertEqual(
                    archive.read("skills/blueprint/SKILL.md"),
                    (ROOT / "skills/blueprint/SKILL.md").read_bytes()
                )
        finally:
            os.unlink(probe)

    def test_manifest_consistency_and_no_execution_capability(self):
        with zipfile.ZipFile(self.output) as archive:
            top = json.loads(archive.read("plugin.json"))
            sub = json.loads(archive.read(".codex-plugin/plugin.json"))
        self.assertEqual(top["version"], sub["version"])
        self.assertEqual(top["extensions"]["com.openai"]["interface"], sub["interface"])
        self.assertEqual(sub["skills"], "./skills")
        self.assertEqual(top["extensions"]["com.openai"]["interface"]["capabilities"], [])
        self.assertNotIn("OpenCode coordination", top["extensions"]["com.openai"]["interface"]["longDescription"])

    def test_hidden_local_edits_are_rejected_before_archive_creation(self):
        import shutil
        for flag in ("--assume-unchanged", "--skip-worktree"):
            for path in ("skills/probe/SKILL.md", "packaging/arca-development/plugin.json",
                         "packaging/arca-development/.codex-plugin/plugin.json"):
                with self.subTest(flag=flag, path=path), tempfile.TemporaryDirectory() as directory:
                    fixture = Path(directory)
                    shutil.copytree(ROOT / "packaging", fixture / "packaging")
                    skill = fixture / "skills/probe/SKILL.md"
                    skill.parent.mkdir(parents=True)
                    skill.write_text("---\nname: probe\ndescription: Disposable packaging fixture\n---\n")

                    def git(*args):
                        subprocess.run(["git", "-C", str(fixture), *args], check=True,
                                       capture_output=True)

                    git("init", "-q")
                    git("add", ".")
                    git("-c", "user.name=Packaging Fixture", "-c",
                        "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                        "commit", "-qm", "Disposable local test fixture")
                    git("update-index", flag, path)
                    target = fixture / path
                    probe = b"\n \t" if target.suffix == ".json" else b"\nUNCOMMITTED LOCAL PROBE\n"
                    target.write_bytes(target.read_bytes() + probe)
                    output = fixture / "candidate.zip"
                    result = subprocess.run(
                        [sys.executable, str(fixture / "packaging/build_candidate.py"),
                         "--out", str(output)], capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Candidate source differs from Git HEAD", result.stderr)
                    self.assertFalse(output.exists())

    def test_reproducible_and_non_overwriting_archive(self):
        copy = Path(self.temp.name) / "second.zip"
        subprocess.run([sys.executable, str(BUILDER), "--out", str(copy)], check=True, capture_output=True)
        self.assertEqual(self.output.read_bytes(), copy.read_bytes())
        failure = subprocess.run([sys.executable, str(BUILDER), "--out", str(copy)], capture_output=True)
        self.assertNotEqual(failure.returncode, 0)


if __name__ == "__main__":
    unittest.main()
