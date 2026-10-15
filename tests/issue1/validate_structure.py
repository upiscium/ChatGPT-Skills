"""Validate skill packaging only; behavioral evidence comes from fresh agent use.

Run from a checkout with Python 3 and PyYAML:
    python tests/issue1/validate_structure.py --base <pre-change-ref>
The base identifies pre-existing packaging gaps; it is not an approval source.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

import yaml


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    root = Path(git("rev-parse", "--show-toplevel"))
    baseline = set(git("ls-tree", "-r", "--name-only", args.base).splitlines())
    paths = set(git("diff", "--name-only", args.base).splitlines())
    paths.update(git("ls-files", "--others", "--exclude-standard").splitlines())
    names = sorted({p.split("/")[1] for p in paths if p.startswith("skills/")})
    preexisting = []
    for name in names:
        folder = root / "skills" / name
        skill = (folder / "SKILL.md").read_text()
        metadata = yaml.safe_load(skill.split("---", 2)[1])
        assert set(metadata) == {"name", "description"}, name
        assert metadata["name"] == name and metadata["description"], name
        assert len(skill.splitlines()) < 500, name
        ui = yaml.safe_load((folder / "agents/openai.yaml").read_text())
        assert "$" + name in ui["interface"]["default_prompt"], name
        for key in ("icon_small", "icon_large"):
            if key not in ui["interface"]:
                continue
            target = folder / ui["interface"][key]
            if target.is_file():
                continue
            rel_ui = f"skills/{name}/agents/openai.yaml"
            old = yaml.safe_load(git("show", f"{args.base}:{rel_ui}"))
            target_rel = str(target.relative_to(root))
            assert old["interface"].get(key) == ui["interface"][key], (name, key)
            assert target_rel not in baseline, target_rel
            preexisting.append({"path": rel_ui, "field": key, "missing": target_rel})
        for md in folder.rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", md.read_text()):
                if not re.match(r"^(https?:|#)", link):
                    assert (md.parent / link.split("#")[0]).exists(), (md, link)
    schema = (root / "skills/repo-handoff/references/state-schema.md").read_text()
    json.loads(re.search(r"```json\n(.*?)\n```", schema, re.S).group(1))
    old = git("show", f"{args.base}:skills/human-review/SKILL.md")
    new = (root / "skills/human-review/SKILL.md").read_text()
    pattern = r"## Output no-review state.*?```markdown\n(.*?)\n```"
    assert re.search(pattern, old, re.S).group(1) == re.search(pattern, new, re.S).group(1)
    subprocess.run(["git", "diff", "--check", args.base], check=True)
    print(json.dumps({"result": "pass", "scope": "structural-only", "skills": names,
                      "preexisting_asset_gaps": preexisting,
                      "behavioral_evidence": "not established by this validator"}, indent=2))


if __name__ == "__main__":
    main()
