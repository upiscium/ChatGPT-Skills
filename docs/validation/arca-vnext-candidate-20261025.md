# Arca Development vNext — source-only candidate packaging

Target: [Arca Issue #4](https://github.com/upiscium/ChatGPT-Skills/issues/4), building on merged source PRs #3 and #5. This is a **buildable, uninstalled candidate**, not an update to the current private v0.1.0 Plugin. The candidate version string `0.2.0-rc.1` is provisional and does not grant publication.

## What is retained and changed

- Single source of truth: the repository's `skills/` tree plus two candidate manifests in `packaging/arca-development/`. No second full copy of all Skill sources.
- Ported the three v0.1.0 Plugin-local contracts (Feature Contract, Scope Change Gate and Feature Acceptance Gate) into `skills/human-review/references/` as optional, lazy-loaded, MVI-scoped references. A material goal/Issue revision may need their fields; routine authorized repairs and unchanged approvals do not create new Human Asks.
- New default: Arca handles user requirements, Issue-level specifications and original-goal acceptance. KAGARI owns implementation, Task technical review/correction and native Ask. MUSUBI consumes KAGARI Task/Ask. The installed package's old broad OpenCode-coordination prompts are replaced in the candidate manifests.
- Legacy implementation/review Skills are **retained but explicit-only**. Do not delete them until real KAGARI/MUSUBI end-to-end acceptance confirms the replacement; no automatic migrations or live connectors are introduced.
- Removed invalid repo-review icon references rather than including an unrelated decorative asset.

## Build in an isolated copy (never installs or publishes)

```bash
python3 packaging/build_candidate.py --out /tmp/arca-development-v0.2.0-rc.1.zip
python3 -m unittest discover -s tests/efficiency-mvi -p 'test_*.py' -v
python3 -m unittest discover -s tests/issue4 -p 'test_*.py' -v
```

Output is a deterministic archive with only the two manifests and current `skills/` files; no source tests, evidence, external connectors, production configuration or plugin-update side effects. The build refuses to overwrite an existing ZIP.

## Acceptance that is still missing

1. Independent source/packaging review of this candidate's exact commit, plus static packaging tests and deterministic build.
2. In a **separate explicitly approved isolated Plugin installation**, verify actual Skill resolution and requirement → Issue → KAGARI-not-dispatched behavior; distinguish candidate UI from old v0.1.0.
3. When KAGARI #291/#292 exposes a verified real supported interface, test one approved Issue through Task/Evidence and Arca's user-goal acceptance. MUSUBI's frontend is not a prerequisite for the first CLI-only end-to-end check.
4. Compare meaningful user interventions, requirement rework and task outcomes against direct OpenCode; record actual token or loaded Skill costs only where telemetry is available.

Do not infer actual savings from Skill root byte counts or a source test. No Plugin Creator update, Release, Task launch or Merge is authorized by this package build.
