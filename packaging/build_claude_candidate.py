"""Build an isolated Claude Code plugin candidate from canonical Arca Skills.

No login, model call, credential access, installation or repository mutation.
The existing OpenAI/Codex build_candidate.py and arca-development ID are untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("packaging/arca-devskills/.claude-plugin/plugin.json")
PLUGIN = "arca-devskills"
SKILLS = (
    "blueprint",
    "human-review",
    "issue-filer",
    "repo-handoff",
    "repo-status",
    "handover",
)
LEGACY_REFERENCES = frozenset(
    {
        "btw",
        "change-review",
        "dev-loop",
        "opencode-bridge",
        "opencode-reviewer",
        "patch-plan",
        "pr-merge",
        "repo-review",
        "security-audit",
        "security-plan",
        "workspace-cleanup",
    }
)
SUPPORTED_MANIFEST_FIELDS = frozenset(
    {
        "name",
        "displayName",
        "version",
        "description",
        "author",
        "repository",
    }
)
SKILL_REFERENCE = re.compile(r"(?<![\w@])@([a-z][a-z0-9-]*)")
LOCAL_REFERENCE = re.compile(r"\]\((references/[^)#?\s]+)(?:#[^)]*)?\)")

ADAPTER_NOTE = """\
> **Claude Code packaging note.** This is an Arca DevSkills skill, adapted
> from the canonical source with only skill-reference syntax changed.
> Packaged skills use /arca-devskills:skill-name. Mentions of an
> "unbundled legacy skill" are informational, NOT installed commands.
> Do not substitute arbitrary Bash or another installed plugin for them.
> Arca owns requirements, Issue drafts and original-goal acceptance only.
> GitHub writes and KAGARI dispatch require their own explicit Human grants.
> KAGARI owns all Task execution, technical review, runtime Ask and Evidence.
> A successful read or prepared Issue does not authorize implementation.

"""

README = """# Arca DevSkills — Claude Code source candidate

This is an uninstalled, source-only, deliberately limited candidate.
It contains six requirements/acceptance skills from ChatGPT-Skills.
The old OpenAI/Codex Arca Development identity and packages are unchanged.

Use 'claude plugin validate --strict <extracted-directory>' for offline checks.
Do not install, run models, file issues or dispatch KAGARI merely from this ZIP.
Further E2E and publication require separate Human authorization.

Unbundled legacy execution/review/merge workflows are not included.
Textual references to them are deliberately inert, not alternate entrypoints.
"""


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        capture_output=True,
        check=False,
        timeout=15,
    )
    if proc.returncode:
        raise ValueError("Git state unavailable for Claude candidate")
    return proc.stdout.strip()


def _source_bytes(path: Path) -> bytes:
    absolute = ROOT / path
    if any(
        part.is_symlink()
        for part in (absolute, *absolute.parents)
        if part != ROOT.parent
    ):
        raise ValueError("Symlink in candidate source: " + path.as_posix())
    if not absolute.is_file() or not absolute.resolve().is_relative_to(ROOT):
        raise ValueError("Missing or out-of-root source: " + path.as_posix())
    if absolute.stat().st_size > 256_000:
        raise ValueError("Oversized candidate source: " + path.as_posix())
    return absolute.read_bytes()


def _text(path: Path) -> str:
    return _source_bytes(path).decode("utf-8")


def _input_sources() -> tuple[Path, ...]:
    """Read-set for the candidate and the builder that fixes its transformation."""
    sources = {MANIFEST, Path("packaging/build_claude_candidate.py")}
    for name in SKILLS:
        folder = Path("skills") / name
        sources.add(folder / "SKILL.md")
        references = ROOT / folder / "references"
        if references.is_dir():
            sources.update(p.relative_to(ROOT) for p in references.rglob("*.md"))
    return tuple(sorted(sources))


def _verify_committed_source(path: Path, *, head: str | None = None) -> None:
    """Check bytes against a pinned commit, even if Git index flags hide edits."""
    revision = head if head is not None else _git("rev-parse", "HEAD")
    local = _source_bytes(path)
    obj = subprocess.run(
        ["git", "-C", str(ROOT), "show", revision + ":" + path.as_posix()],
        capture_output=True,
        check=False,
        timeout=15,
    )
    if obj.returncode or obj.stdout != local:
        raise ValueError(
            "Source is uncommitted or differs from HEAD: " + path.as_posix()
        )


def _verify_committed_sources(head: str) -> None:
    for path in _input_sources():
        _verify_committed_source(path, head=head)


def _adapt(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in SKILLS:
            return "/" + PLUGIN + ":" + name
        if name in LEGACY_REFERENCES:
            return "[unbundled legacy skill: " + name + "]"
        raise ValueError("Unreviewed skill dependency: " + name)

    return SKILL_REFERENCE.sub(replace, text)


def _validate_local_links(text: str, folder: Path) -> None:
    for link in LOCAL_REFERENCE.findall(text):
        rel = Path(link)
        if ".." in rel.parts or not rel.parts or rel.parts[0] != "references":
            raise ValueError("Unsafe skill-local link: " + link)
        _text(folder / rel)


def candidate_files() -> tuple[dict[str, bytes], dict]:
    manifest = json.loads(_text(MANIFEST))
    if set(manifest) - SUPPORTED_MANIFEST_FIELDS:
        raise ValueError("Unexpected Claude manifest capability")
    if (
        manifest.get("name") != PLUGIN
        or manifest.get("displayName") != "Arca DevSkills"
    ):
        raise ValueError("Unexpected Claude plugin identity")
    if not isinstance(manifest.get("version"), str) or not manifest["version"]:
        raise ValueError("Missing Claude candidate version")
    if not isinstance(manifest.get("author"), dict):
        raise TypeError("Missing Claude candidate author")

    files = {
        ".claude-plugin/plugin.json": _text(MANIFEST).encode("utf-8"),
        "README.md": README.encode("utf-8"),
    }
    for name in SKILLS:
        folder = Path("skills") / name
        original = _text(folder / "SKILL.md")
        expected = "---\nname: " + name + "\n"
        if not original.startswith(expected):
            raise ValueError("Missing or mismatched Skill frontmatter: " + name)
        closing = original.find("\n---\n", len(expected))
        if closing < 0:
            raise ValueError("Missing frontmatter boundary: " + name)
        _validate_local_links(original, folder)
        prefix = original[: closing + 5]
        remainder = original[closing + 5 :]
        adapted = _adapt(prefix + ADAPTER_NOTE + remainder)
        files[(folder / "SKILL.md").as_posix()] = adapted.encode("utf-8")
        references = ROOT / folder / "references"
        if references.is_dir():
            for source in sorted(references.rglob("*.md")):
                relative = source.relative_to(ROOT)
                original_reference = _text(relative)
                _validate_local_links(original_reference, relative.parent)
                files[relative.as_posix()] = _adapt(original_reference).encode("utf-8")
    return files, manifest


def build(output: Path, *, preview_uncommitted: bool = False) -> dict:
    head = _git("rev-parse", "HEAD")
    if not preview_uncommitted:
        if _git("status", "--porcelain"):
            raise ValueError(
                "Dirty checkout: use explicit --preview-uncommitted only for isolated tests"
            )
        _verify_committed_sources(head)
    files, manifest = candidate_files()
    memory = io.BytesIO()
    with zipfile.ZipFile(
        memory,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for name in sorted(files):
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o644 << 16
            archive.writestr(
                entry, files[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9
            )
    payload = memory.getvalue()
    target = output.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(payload)
    return {
        "artifact": str(target),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "source_head": head,
        "preview_uncommitted": preview_uncommitted,
        "version": manifest["version"],
        "skills": list(SKILLS),
        "files": len(files),
        "bytes": len(payload),
        "installed_plugin_modified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preview-uncommitted", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            build(args.out, preview_uncommitted=args.preview_uncommitted),
            sort_keys=True,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
