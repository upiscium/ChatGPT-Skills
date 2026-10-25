"""Build a deterministic source-only Arca candidate ZIP, without installing it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "packaging" / "arca-development"


def entries():
    """Return (archive name, on-disk source) for the actual candidate package."""
    manifests = {
        "plugin.json": MANIFEST_DIR / "plugin.json",
        ".codex-plugin/plugin.json": MANIFEST_DIR / ".codex-plugin" / "plugin.json",
    }
    # Ship only the committed source. Local scratch files under skills/ are not part
    # of a GitHub-pinned candidate, even if they happen to exist in this checkout.
    tracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "-z", "--", "skills"]
    )
    changed = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--",
         "skills", "packaging/arca-development"],
        check=False,
    )
    if changed.returncode:
        raise ValueError("Tracked candidate sources differ from Git HEAD; commit or restore before building")
    files = dict(manifests)
    for entry in tracked.split(b"\0"):
        if not entry:
            continue
        name = entry.decode("utf-8")
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(f"Git-tracked Skill file missing: {name}")
        files[name] = path
    skill_roots = sorted(name for name in files if name.startswith("skills/") and name.endswith("/SKILL.md"))
    if not skill_roots:
        raise ValueError("No Git-tracked Skill entrypoints found")
    payloads = {}
    for name, path in files.items():
        if not path.is_file():
            raise FileNotFoundError(f"{name}: {path}")
        # Git's stat/index flags can hide local edits from `git diff`. Compare
        # actual bytes with HEAD and retain those same bytes for ZIP assembly.
        payload = path.read_bytes()
        committed = subprocess.check_output(
            ["git", "-C", str(ROOT), "show", f"HEAD:{path.relative_to(ROOT).as_posix()}"]
        )
        if payload != committed:
            raise ValueError(f"Candidate source differs from Git HEAD: {path.relative_to(ROOT)}")
        payloads[name] = payload
    top = json.loads(payloads["plugin.json"])
    codex = json.loads(payloads[".codex-plugin/plugin.json"])
    for key in ("name", "version", "description", "author", "repository"):
        if top.get(key) != codex.get(key):
            raise ValueError(f"Manifest mismatch: {key}")
    if top["extensions"]["com.openai"]["interface"] != codex["interface"]:
        raise ValueError("Manifest UI mismatch")
    if codex["skills"] != "./skills":
        raise ValueError("Unexpected Skill package root")
    return sorted(payloads.items()), len(skill_roots), top["version"]


def build(output: Path):
    file_entries, skill_count, version = entries()
    output = output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite an existing artifact: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, source in file_entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o644 << 16)
            archive.writestr(info, source, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return {
        "file": str(output),
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "bytes": output.stat().st_size,
        "files": len(file_entries),
        "skills": skill_count,
        "candidate_version": version,
        "installed_plugin_modified": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Assemble a local, uninstalled Arca vNext candidate ZIP")
    parser.add_argument("--out", type=Path, required=True, help="New output ZIP path (will not overwrite)")
    options = parser.parse_args()
    print(json.dumps(build(options.out), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
