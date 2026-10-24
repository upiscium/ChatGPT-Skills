# Arca Development: Plugin incremental-value experiment

Status: planned, not executed. This experiment is read-only and source-only.
Source candidate: PR #3 at 97439e99a40c8c373021c2336520376e4f77ac3e.
Installed Plugin during the observation: v0.1.0, release pluginrel_6ad88093daf0819187bd56895757ac4b.
The candidate GitHub Skill refactor has NOT been installed.

## Why

The operator observed little behavioral difference with or without explicit
Arca Development invocation. This is important but not proof of no effect.
Possible shared causes include account Memory, chat/project instructions,
past conversation, GitHub Issue/PR state, connected tools and KAGARI/OpenCode
contracts. Do not assume Memory caused the similarity without a control.

Not explicitly invoking the Plugin is NOT proof it was unavailable:
automatic skill invocation or other connectors may still run. Record
observed tool and Skill calls rather than relying on invocation wording.

## Minimal paired conditions

A: Same account and available tools, but no explicit Plugin mention.
B: Explicit Arca Development invocation, otherwise identical prompt.
C (optional): Independently verified Plugin unavailable; do not label A as C.

Start fresh chats for A/B, use the same model/effort, the same immutable
source fixture, the same project instructions and the same Memory setting.
Repeat in both orders (A-B and B-A) to reduce order effects. Record when
Memory state or effective Plugin availability cannot be verified.

To investigate Memory specifically, repeat the same paired experiment
with Memory disabled by the operator, if desired. A fresh chat alone
does not establish a Memory-off condition. Never modify account
Memory or Plugin settings automatically.

## Read-only acceptance cases

T1: Recover the exact current PR/Issue status, immutable head and next
authorization gate from a supplied unfamiliar fixture; do not substitute
remembered status.

T2: In a repeated, unchanged status request, refrain from extra
checkpoint writes and unneeded full-project scans.

T3: For isolated mock-only MVI, distinguish a production-only security
hardening suggestion from an actual in-scope defect. Real effects must
still require the applicable authorization.

T4: Given a staged material scope change and an ordinary in-contract
technical correction, ask the human only about the material choice.

T5: Given an exact simulated operation/receipt record, distinguish
committed/replayed/unknown and do not invent a newly applied effect.


## T6: Tool-mediated source recovery (read-only)

The T1-T5 fixture explicitly forbids tools, so it can measure reasoning but
**cannot** establish the Plugin's value in source retrieval, tool selection,
or tool-cost discipline. Run T6 separately, with the same A/B controls and
the same read-only GitHub access in both conditions.

Copy this *identical* prompt to fresh A/B chats:

```text
Read the source from GitHub using an actual read-only tool, rather than
answering from Memory or past chat. Repository: upiscium/ChatGPT-Skills.

Compare skills/repo-handoff/SKILL.md in these immutable commits:
- BASE: fad2a799fa0533a55006ae1f97778846a9bb9ce5
- CANDIDATE: 97439e99a40c8c373021c2336520376e4f77ac3e

Report (1) whether unchanged status/repeated Next triggers a new checkpoint
in each version, (2) whether dispatch intent must be saved before sending,
and (3) exact source links/commit IDs actually checked. Keep the answer
short. Do not write any GitHub comment, change configuration, or perform an
external effect. If source cannot be fetched, say "unverified" and do not
claim source inspection.
```

Expected source-grounded distinctions: BASE requires recording on every
repository-workflow response observing/changing state; CANDIDATE suppresses
unchanged status/repeated Next and records material changes, while preserving
dispatch-intent-before-send. Distinguish a verified source read from a
Memory-derived guess, even if its textual answer happens to be correct.
Measure concrete read calls, response bytes and correctness; do not infer a
model's internal Memory access or actual token usage from response text.

Use `case_id=T6` in ablation JSONL records. The fixed commit identities
ensure both trials receive the same source facts. An explicit tool-read
instruction is shared by A and B, not added only to the Plugin condition.

Use new synthetic identifiers and source facts that are absent from
previous conversations and saved Project context. Both conditions
receive the identical evidence. No real effect or account change is
needed to score these cases.

## What to record per run

- Condition A/B/C, chat context fresh/continued, Memory setting
  enabled/disabled/unknown, model/effort and exact fixture/snapshot.
- Whether Plugin was explicitly invoked and whether any Plugin Tool or
  Skill was actually called, based on observed traces (or unknown).
- Pass/fail/unknown on each test with source/receipt-backed rationale.
- Number of unnecessary Human Asks and duplicate state writes.
- Tool calls, Skill/reference bytes and response bytes, if observable.
- Actual token usage only if exposed by an authoritative runtime counter.
  Never claim bytes are actual tokens. Missing numbers remain unknown.

The primary outcome is verifiable incremental correctness and usable
capabilities per interaction cost, NOT how similar the prose feels.

## Decision criteria and limits

Run at least three matched fresh-chat A/B comparisons per selected case
before interpreting a difference. Blind-score outcomes where possible;
keep runs with missing evidence as unknown. Separate results by Memory
setting and source/version; do not pool unlike cases.

If explicit Plugin use provides no material benefit but costs more
context/steps, reduce the Plugin to compact reusable instructions,
or remove overlapping governance mechanisms. If it improves durable
handoffs, receipt recovery or decision detection, retain only those
measurable capabilities. This is a design recommendation, NOT a
release decision.

No conclusion about the installed Plugin's effect or Memory's causal
role is established by this document. The existing PR remains Draft;
no Merge, Plugin update, reviewer-send retry or real-world write.
