# PR #5 — independent source review, 2026-10-25

## Target and scope

- Repository: upiscium/ChatGPT-Skills; Draft PR #5.
- Original reviewed head: `3b7046950b36408b5118f023ed2287052e62cfad`.
- Base: `2abb001507d0a99a74ffb6078c8421a58bae8acd`.
- Authority: [ChatGPT-Skills #4](https://github.com/upiscium/ChatGPT-Skills/issues/4), [KUMIKI #291](https://github.com/upiscium/KUMIKI/issues/291), [KUMIKI #292](https://github.com/upiscium/KUMIKI/issues/292), [MUSUBI #1](https://github.com/upiscium/MUSUBI/issues/1), and the current user's explicit review/bounded-correction instruction.
- Mode: PR/source-only; risk medium. Base-stable for the reported finding, subject to rechecking shared callers if base/contracts change.
- Scope is this first declarative Arca slice. Issue #4 remains partial/open; real KAGARI/MUSUBI integration and comparative live development-task acceptance are not claimed.

A fresh read-only Work/Codex reviewer inspected the complete PR diff, upstream Issue contracts, selected Issue #4 checkpoint and relevant transitive callers/references/UI metadata. The implementer's tests and source assertions were treated as claims. A separate correction checkout preserved the immutable original snapshot. All 121 downloaded/copied skills/tests blobs were verified against GitHub blob identities. Upstream tree contained no AGENTS.md/README/contribution instructions.

**No OpenCode Reviewer/session startup was attempted.** The formerly safety-blocked route remains unexecuted. This review used the explicitly authorized fresh Work context and read-only local sources; no more-privileged role, alternate OpenCode transport or runtime workaround was used.

## Independent finding and correction

### PR-001 — transitive callers still select legacy planning/repair

Original recommendation: **changes-required**. Priority P2, blocking, high confidence.

Original-head locations:

- `skills/blueprint/SKILL.md:112` assigns execution steps to patch-plan after Issue selection.
- `skills/blueprint/references/design-brief-template.md:97`, mandatory from blueprint, repeats the unconditional patch-plan handoff.
- `skills/debug-investigate/SKILL.md:8` owns diagnosis and repair handoff through patch-plan/dev-loop/opencode-bridge, while its metadata still permits implicit invocation.

A new requirement can follow the new default dev-loop through blueprint into old execution planning. A normal KAGARI delivery defect can implicitly select Arca diagnosis/legacy repair, or stall against patch-plan's explicit-legacy restriction. Disabling invocation on leaf skills alone does not isolate their callers. This contradicts Issue #4's KAGARI Task ownership and explicit-only compatibility.

Minimum correction applied in five files:

1. Blueprint description and execution-owner bullet now name KAGARI/Task Orchestrator for the exact Human-authorized Issue set; patch-plan is explicitly selected legacy work.
2. The mandatory design template preserves the same distinction and states that Issue creation alone does not authorize execution.
3. Debug investigation returns ordinary in-spec failures/evidence to the existing KAGARI Task. Independently requested bounded diagnosis remains available; old OpenCode repair transport requires explicit legacy selection.
4. Debug UI metadata is consistent and disallows implicit invocation.
5. The existing metadata regression now includes debug-investigate.

Focused independent re-review **closed PR-001 with no new material findings**. Shared stale SwitchBoard language outside this correction was not established as an actual independent monitoring path and was not promoted into a new blocker or expanded refactor.

## Corrected source identity

SHA-256 manifest over sorted UTF-8 lines `<sha256>  <relative-path>\n`:

`591b34d41433cb11e08fc93ea040712391bb7e1e3384ce9cddca8e76d11f92ae`.

| File | SHA-256 |
| --- | --- |
| skills/blueprint/SKILL.md | 07e5c1745c8f6ab3f543fe4a22a9589c5bff7dd8e83d010377b732b10828de1d |
| skills/blueprint/references/design-brief-template.md | 04a072a85e7c46caf8bf1a9280c40df35fc871c78501cec45ecc4278fc883d03 |
| skills/debug-investigate/SKILL.md | 63b4d3b031f93d106a96e0426a80074295e00afab05e984bd1a1f58484f01d81 |
| skills/debug-investigate/agents/openai.yaml | 10943849038dd409efc6eb13f1fc67b315e3ceef3a9d22dce6ac7013f75f4d61 |
| tests/issue4/test_role_transition.py | 6d457415172412735ffc2cae6942dfa4a5214f739d6c1a026f81396d0c63e7c5 |

The parent PR head carrying this report must be read back and verified equivalent before treating the correction as published.

## Acceptance traceability

IDs below are **review-derived labels**, not new repository authority or fabricated approved AC IDs.

| Criterion from upstream contracts | Inspected mechanism/evidence | Result |
| --- | --- | --- |
| R1 Material questions and first human alignment | blueprint + default requirements reference; requirements source exercise | Source satisfied |
| R2 Function-level Issue specs, observable ACs, exclusions | issue-filer and design template | Source satisfied |
| R3 Exact-set second alignment, separate execution authorization | default dev-loop, requirements reference, issue-filer handoff; no invented CLI | Source satisfied |
| R4 KAGARI execution/tests/technical review/correction ownership | corrected blueprint/template/debug handoffs; acceptance source exercise | Source satisfied after PR-001 |
| R5 Explicit-only old OpenCode routing, including callers/UI | corrected debug metadata; existing patch-plan/bridge/reviewer/change-review flags; legacy content retained | Source satisfied after PR-001 |
| R6 Arca original-goal acceptance with actual evidence | repo-review default + four outcome classes; acceptance source exercise | Source satisfied |
| R7 KAGARI Ask state, MUSUBI frontend, no independent Arca watcher | default owner declarations; #291/#292 and MUSUBI #1 boundaries | Source satisfied; integration unverified |
| R8 Remove arbitrary stage throttle without new grants | dev-loop root/governance; exact human alignment and Issue-set boundaries retained | Source satisfied |
| R9 Real KAGARI output, installed Plugin behavior and direct-OpenCode development baseline | No runtime adapter/installation executed in this slice | Unverified, explicitly deferred |

## Validation

Environment: Work container, Python 3.12.14 and PyYAML.

- Original head: efficiency/policy suite **22/22 PASS**, Issue #4 suite **9/9 PASS**, independently rerun.
- Corrected snapshot: both suites **31/31 PASS**, independently rerun by the focused reviewer.
- Sensitivity: expanded metadata test fails against the original snapshot specifically on implicit debug-investigate, then passes on the correction.
- Structural validator **PASS**, with the same two pre-existing repo-review icon-reference gaps. Markdown references and diff whitespace checks passed.
- Skill Creator quick validation: corrected blueprint and debug-investigate **PASS**; UI prompts were checked against their source boundaries.
- Structural validation used a local content-equivalent skills/tests base tree `a73ec6f2cc0c71b1592ba01e267f55c6b5a41325`, reconstructed by reversing the complete PR diff, not an upstream commit.
- Original-head GitHub check-runs API: GitGuardian Security Checks completed/success. No submitted reviews, inline review comments or PR workflow runs were returned during initial restore. A passing secret check is not behavioral acceptance.
- No broadened integration tests or production probes were run.

Commands:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/efficiency-mvi -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/issue4 -p 'test_*.py' -v
python3 tests/issue1/validate_structure.py --base <content-equivalent-base-tree>
```

## Supplemental source exercises

Two additional fresh read-only agent contexts were given the candidate Skill and task-local fictional facts, without the finding, intended fix, test oracle or coordinator conclusions. They used candidate files rather than installed same-name Plugin instructions. No outside tools, Issue writes or Task execution were permitted.

**Requirements exercise:** Eight students need a mobile reservation tool for one room with no overlaps; only specification drafts requested. The actor returned an explicitly unapproved draft, grouped material questions about usage rules, a first user alignment request, observable ACs and exclusions. Issue posting and execution stayed separate; KAGARI execution was not-dispatched and required an exact selected Issue set. No old execution packet or direct OpenCode command was produced.

**Acceptance exercise:**

| Raw supplied fact | Actor classification / next owner |
| --- | --- |
| Original goal includes phone editing, but approved Issue and delivered create/list omit editing | specification-goal-mismatch → User/Arca affected specification correction |
| Approved available-time path returns reproducible HTTP 500, existing Task owns ordinary corrections | in-spec-defect → existing KAGARI Task, no extra ordinary repair approval |
| Mobile readability has CI PASS only and no UI evidence | unknown → minimum UI/operation evidence from owning Task |
| Direct phone trace proves overlap rejection with explanation and valid booking success | goal-satisfied → no further action for that goal |

The actor retained all next-Issue/phase/Merge/release boundaries. These source exercises support the narrow instruction routes; they are **not installed Plugin acceptance, a live KAGARI workflow, causal proof of the fix or a comparative efficacy benchmark**.

## Review conclusion and next gate

The material source finding is resolved at the correction manifest above. The full original-head review plus focused correction review supports a **source-only ready** recommendation once exact PR publication equivalence and live base/head/checks are verified. No unresolved human architecture/scope decision was found in this bounded correction.

Next gate: any Merge requires the user's separate explicit authorization at the current immutable head. Recheck base/head, available checks and source equivalence; keep Draft and preserve current installed Plugin if no grant is given. Plugin update/publication, live KAGARI/MUSUBI acceptance and production operations are separate work and were not performed. Do not close Issue #4 as fully implemented from this first slice.
