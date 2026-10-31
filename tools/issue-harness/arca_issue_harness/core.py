"""Offline deterministic checks and rendering for standalone Issue drafts.

Security boundary:
* The model supplies a candidate, NOT the source snapshot or action permissions.
* The source snapshot is loaded from a server-configured read-only directory and
  pinned by its SHA-256. Such a snapshot is still *not* proof of Human approval.
* No GitHub, Task, code, filesystem write, or other side-effect operation exists.
* Semantic entailment is NOT proved by this structural contract checker.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SNAPSHOT_VERSION = "arca.issue-harness.snapshot.v1"
CANDIDATE_VERSION = "arca.issue-harness.candidate.v1"
ACTIONS = (
    "issue_filing", "task_dispatch", "code_change", "merge", "release", "plugin_update"
)
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{1,63}$")
SNAPSHOT_RE = re.compile(r"^BP-[A-Za-z0-9_-]{2,60}/r[1-9][0-9]*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
CANDIDATE_RE = re.compile(r"^DES-[0-9]{3,5}$")
AC_RE = re.compile(r"^AC-[0-9]{3,5}-[0-9]{2,4}$")
REQUIRED_REVALIDATION = (
    "source_snapshot", "target_revision", "human_action_approval", "open_decisions"
)
MAX_SNAPSHOT_BYTES = 131_072
MAX_CANDIDATE_BYTES = 65_536


def snapshot_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _issue(code: str, location: str, detail: str) -> dict[str, str]:
    return {"code": code, "location": location, "detail": detail}


def _short_text(value: Any, location: str, errors: list[dict[str, str]]) -> str:
    if (not isinstance(value, str) or not value or len(value) > 2048
            or value != value.strip() or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        errors.append(_issue("INVALID_TEXT", location, "Required one-line, trimmed, non-control text (1-2048 chars)."))
        return ""
    return value


def _md(value: str) -> str:
    """Escape model-authored text as a literal CommonMark/GFM fragment.

    List entries must not become nested headings/lists, and GFM must not
    autolink bare URLs or email addresses supplied by a candidate.
    """
    escaped = (value.replace("\\", "\\\\").replace("&", "&amp;")
               .replace("<", "&lt;").replace(">", "&gt;"))
    # GFM autolinks need uninterrupted URL/email punctuation, including
    # colon, dot and @. Escape those, plus block/list Markdown markers.
    for mark in chr(96) + "*_[]()!|~#.+@:":
        escaped = escaped.replace(mark, "\\" + mark)
    if escaped.startswith("-"):
        escaped = "\\" + escaped
    return escaped


def _keys(value: Any, allowed: set[str], required: set[str], location: str,
          errors: list[dict[str, str]]) -> bool:
    if not isinstance(value, dict):
        errors.append(_issue("TYPE", location, "Expected JSON object."))
        return False
    for key in sorted(set(value) - allowed):
        errors.append(_issue("UNKNOWN_FIELD", f"{location}.{key}", "Unsupported field (fail closed)."))
    for key in sorted(required - set(value)):
        errors.append(_issue("MISSING_FIELD", f"{location}.{key}", "Required field is missing."))
    return not (set(value) - allowed or required - set(value))


def _text_list(value: Any, location: str, errors: list[dict[str, str]], *, nonempty: bool = True) -> list[str]:
    if (not isinstance(value, list) or (nonempty and not value) or len(value) > 64):
        errors.append(_issue("INVALID_LIST", location, "Expected a bounded list of text entries."))
        return []
    result = [_short_text(v, f"{location}[{i}]", errors) for i, v in enumerate(value)]
    if len(set(result)) != len(result):
        errors.append(_issue("DUPLICATE", location, "Duplicate entries are not allowed."))
    return result


def _digest_candidate(candidate: Any) -> str | None:
    try:
        return hashlib.sha256(_canonical(candidate)).hexdigest()
    except (TypeError, ValueError):
        return None


class Harness:
    def __init__(self, snapshots_dir: Path):
        self.snapshots_dir = Path(snapshots_dir).resolve(strict=True)
        if not self.snapshots_dir.is_dir():
            raise ValueError("snapshots_dir must be an existing directory")

    def _load_snapshot(self, source_id: str, sha256: str) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
        errors: list[dict[str, str]] = []
        if not isinstance(source_id, str) or not SNAPSHOT_RE.fullmatch(source_id):
            return None, [_issue("INVALID_SOURCE_ID", "source_id", "Expected BP-.../rN identifier; no path input.")]
        if not isinstance(sha256, str) or not SHA_RE.fullmatch(sha256):
            return None, [_issue("INVALID_DIGEST", "source_sha256", "Expected lower-case SHA-256 hex.")]
        name = source_id.replace("/", "__") + ".json"
        path = self.snapshots_dir / name
        # Do not follow symlinks: a caller cannot induce an escape into other files.
        if path.is_symlink() or not path.is_file() or path.parent.resolve() != self.snapshots_dir:
            return None, [_issue("SOURCE_UNAVAILABLE", "source_id", "Pinned source is unavailable.")]
        try:
            raw = path.read_bytes()
            if len(raw) > MAX_SNAPSHOT_BYTES:
                raise ValueError("snapshot too large")
            if hashlib.sha256(raw).hexdigest() != sha256:
                return None, [_issue("SOURCE_DRIFT", "source_sha256", "Pinned source digest mismatch.")]
            snap = json.loads(raw)
        except (OSError, ValueError, UnicodeDecodeError):
            return None, [_issue("INVALID_SOURCE", "source_id", "Source JSON cannot be verified.")]
        _keys(snap, {"schema_version", "source_id", "original_goal", "approval_provenance", "draft_scope",
                     "project_non_goals", "source_claims", "human_decisions", "prohibited_actions"},
              {"schema_version", "source_id", "original_goal", "approval_provenance", "draft_scope",
               "project_non_goals", "source_claims", "human_decisions", "prohibited_actions"}, "snapshot", errors)
        if not isinstance(snap, dict):
            return None, errors
        if snap.get("schema_version") != SNAPSHOT_VERSION or snap.get("source_id") != source_id:
            errors.append(_issue("SOURCE_SCHEMA", "snapshot", "Unexpected schema version or source identity."))
        for key in ("original_goal", "approval_provenance", "draft_scope"):
            _short_text(snap.get(key), f"snapshot.{key}", errors)
        if snap.get("draft_scope") != "draft-only":
            errors.append(_issue("DRAFT_ONLY", "snapshot.draft_scope", "MVI cannot assert execution or filing authority."))
        _text_list(snap.get("project_non_goals"), "snapshot.project_non_goals", errors)
        actions = snap.get("prohibited_actions")
        if not isinstance(actions, list) or len(set(map(str, actions))) != len(actions) or any(x not in ACTIONS for x in actions):
            errors.append(_issue("INVALID_ACTIONS", "snapshot.prohibited_actions", "Only distinct known action IDs are accepted."))
        claims = snap.get("source_claims")
        if not isinstance(claims, list) or not claims or len(claims) > 64:
            errors.append(_issue("INVALID_CLAIMS", "snapshot.source_claims", "Expected nonempty claim list."))
        else:
            ids = []
            for i, item in enumerate(claims):
                loc = f"snapshot.source_claims[{i}]"
                _keys(item, {"id", "text"}, {"id", "text"}, loc, errors)
                if not isinstance(item, dict):
                    continue
                key = item.get("id")
                if not isinstance(key, str) or not ID_RE.fullmatch(key):
                    errors.append(_issue("INVALID_CLAIM_ID", loc, "Invalid claim ID."))
                ids.append(key if isinstance(key, str) else "")
                _short_text(item.get("text"), loc + ".text", errors)
            if len(ids) != len(set(ids)):
                errors.append(_issue("DUPLICATE_CLAIM", "snapshot.source_claims", "Claim IDs must be unique."))
        decisions = snap.get("human_decisions")
        if not isinstance(decisions, list) or len(decisions) > 64:
            errors.append(_issue("INVALID_DECISIONS", "snapshot.human_decisions", "Expected decision list."))
        else:
            ids = []
            for i, item in enumerate(decisions):
                loc = f"snapshot.human_decisions[{i}]"
                _keys(item, {"id", "question", "impact"}, {"id", "question", "impact"}, loc, errors)
                if not isinstance(item, dict):
                    continue
                key = item.get("id")
                if not isinstance(key, str) or not ID_RE.fullmatch(key):
                    errors.append(_issue("INVALID_DECISION_ID", loc, "Invalid decision ID."))
                ids.append(key if isinstance(key, str) else "")
                _short_text(item.get("question"), loc + ".question", errors)
                _short_text(item.get("impact"), loc + ".impact", errors)
            if len(ids) != len(set(ids)):
                errors.append(_issue("DUPLICATE_DECISION", "snapshot.human_decisions", "Decision IDs must be unique."))
        return (None if errors else snap), errors

    def _validate_candidate(self, candidate: Any, snapshot: dict[str, Any]) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        try:
            if len(_canonical(candidate)) > MAX_CANDIDATE_BYTES:
                return [_issue("OVERSIZE", "candidate", "Candidate exceeds size limit.")]
        except (TypeError, ValueError):
            return [_issue("INVALID_JSON", "candidate", "JSON compatible data required.")]
        _keys(candidate, {"schema_version", "id", "revision", "title", "desired_outcome", "scenario",
                          "in_scope", "candidate_exclusions", "acceptance_criteria", "dependencies",
                          "business_revalidations", "human_decision_ids", "evidence", "legacy_revalidation_coverage"},
              {"schema_version", "id", "revision", "title", "desired_outcome", "scenario",
               "in_scope", "candidate_exclusions", "acceptance_criteria", "dependencies",
               "business_revalidations", "human_decision_ids", "evidence"}, "candidate", errors)
        if not isinstance(candidate, dict):
            return errors
        if candidate.get("schema_version") != CANDIDATE_VERSION:
            errors.append(_issue("CANDIDATE_SCHEMA", "candidate.schema_version", "Unexpected version."))
        if not isinstance(candidate.get("id"), str) or not CANDIDATE_RE.fullmatch(candidate["id"]):
            errors.append(_issue("CANDIDATE_ID", "candidate.id", "Expected DES-NNN ID."))
        if not isinstance(candidate.get("revision"), str) or not re.fullmatch(r"r[1-9][0-9]*", candidate["revision"]):
            errors.append(_issue("CANDIDATE_REVISION", "candidate.revision", "Expected rN revision."))
        for field in ("title", "desired_outcome", "scenario"):
            _short_text(candidate.get(field), f"candidate.{field}", errors)
        for field, nonempty in (("in_scope", True), ("candidate_exclusions", False), ("evidence", True)):
            _text_list(candidate.get(field), f"candidate.{field}", errors, nonempty=nonempty)
        src_decisions = {x["id"] for x in snapshot["human_decisions"]}
        ids = candidate.get("human_decision_ids")
        if not isinstance(ids, list) or len(ids) != len(set(map(str, ids))) or any(not isinstance(x, str) or x not in src_decisions for x in ids):
            errors.append(_issue("DECISION_REFS", "candidate.human_decision_ids", "Expected distinct registered Human decisions."))
            ids = []
        # Preserve every project-wide unresolved decision in each standalone output.
        if set(ids) != src_decisions:
            errors.append(_issue("MISSING_DECISION", "candidate.human_decision_ids", "Every source-level unresolved Human decision must remain local."))
        acs = candidate.get("acceptance_criteria")
        status_map: dict[str, str] = {}
        if not isinstance(acs, list) or not acs or len(acs) > 64:
            errors.append(_issue("INVALID_ACS", "candidate.acceptance_criteria", "Expected nonempty list of ACs."))
            acs = []
        claims = {c["id"]: c["text"] for c in snapshot["source_claims"]}
        for i, ac in enumerate(acs):
            loc = f"candidate.acceptance_criteria[{i}]"
            _keys(ac, {"id", "text", "status", "source_claim_id", "decision_id"},
                  {"id", "text", "status"}, loc, errors)
            if not isinstance(ac, dict):
                continue
            ac_id = ac.get("id")
            if not isinstance(ac_id, str) or not AC_RE.fullmatch(ac_id):
                errors.append(_issue("AC_ID", loc, "Expected AC-NNN-NN ID."))
            elif ac_id in status_map:
                errors.append(_issue("DUPLICATE_AC", loc, "AC IDs must be unique."))
            # Each standalone DES owns a local AC namespace. A syntactically
            # valid AC from another DES is not an authorized cross-Issue link.
            candidate_id = candidate.get("id")
            if (isinstance(ac_id, str) and AC_RE.fullmatch(ac_id)
                    and isinstance(candidate_id, str) and CANDIDATE_RE.fullmatch(candidate_id)
                    and ac_id.split("-")[1] != candidate_id.split("-")[1]):
                errors.append(_issue("AC_NAMESPACE", loc + ".id",
                                     "AC ID must use the exact numeric namespace of its DES candidate."))
            _short_text(ac.get("text"), loc + ".text", errors)
            status = ac.get("status")
            if status not in ("confirmed", "derived-unconfirmed"):
                errors.append(_issue("AC_STATUS", loc, "Invalid AC status."))
            if isinstance(ac_id, str):
                status_map[ac_id] = status
            if status == "confirmed":
                claim = ac.get("source_claim_id")
                if not isinstance(claim, str) or claim not in claims or ac.get("text") != claims.get(claim):
                    errors.append(_issue("UNVERIFIED_CONFIRMED_AC", loc, "A confirmed AC must exactly match a pinned source claim."))
                if ac.get("decision_id") is not None:
                    errors.append(_issue("CONFIRMED_DECISION", loc, "Confirmed AC cannot require an unresolved decision."))
            elif status == "derived-unconfirmed":
                if not isinstance(ac.get("decision_id"), str) or ac.get("decision_id") not in src_decisions:
                    errors.append(_issue("UNCONFIRMED_OWNER", loc, "Derived AC requires a known unresolved Human decision."))
                if ac.get("source_claim_id") is not None:
                    errors.append(_issue("UNCONFIRMED_SOURCE", loc, "Derived AC must not claim confirmed source binding."))
        # Optional evidence imported from a historical free-text draft. This is
        # only a caller-reported transcription, not a parser or runtime receipt.
        # A missing coverage field is OK: the renderer constructs the complete
        # action table instead of trusting model-authored free text.
        coverage = candidate.get("legacy_revalidation_coverage")
        if coverage is not None:
            if (not isinstance(coverage, list) or len(coverage) > len(ACTIONS)
                    or any(not isinstance(x, str) or x not in ACTIONS for x in coverage)
                    or len(set(coverage)) != len(coverage)):
                errors.append(_issue("INVALID_LEGACY_COVERAGE", "candidate.legacy_revalidation_coverage",
                                     "Expected distinct action IDs."))
            else:
                missing = sorted(set(snapshot["prohibited_actions"]) - set(coverage))
                if missing:
                    errors.append(_issue("AUTHORITY_REVALIDATION_GAP", "candidate.legacy_revalidation_coverage",
                                         "Historical draft omits pre-action revalidation for: " + ", ".join(missing)))
        for field in ("dependencies", "business_revalidations"):
            refs = candidate.get(field)
            if not isinstance(refs, list) or len(refs) > 64:
                errors.append(_issue("INVALID_REFERENCES", f"candidate.{field}", "Expected bounded list."))
                continue
            for i, item in enumerate(refs):
                loc = f"candidate.{field}[{i}]"
                _keys(item, {"text", "ac_refs", "binding"}, {"text", "ac_refs", "binding"}, loc, errors)
                if not isinstance(item, dict):
                    continue
                _short_text(item.get("text"), loc + ".text", errors)
                refs_list = item.get("ac_refs")
                if not isinstance(refs_list, list) or not refs_list or len(refs_list) > 32:
                    errors.append(_issue("INVALID_AC_REFS", loc, "References must be a nonempty AC list."))
                    continue
                if len(set(map(str, refs_list))) != len(refs_list):
                    errors.append(_issue("DUPLICATE_AC_REFS", loc, "Duplicate AC references."))
                for ref in refs_list:
                    if not isinstance(ref, str) or ref not in status_map:
                        errors.append(_issue("UNKNOWN_AC_REF", loc, "Reference to an unknown AC."))
                binding = item.get("binding")
                if binding not in ("required", "conditional"):
                    errors.append(_issue("INVALID_BINDING", loc, "Expected required or conditional."))
                if binding == "required":
                    if any(not isinstance(ref, str) or status_map.get(ref) != "confirmed" for ref in refs_list):
                        errors.append(_issue("UNCONFIRMED_BINDING", loc, "Derived/unresolved AC cannot become a required dependency or business rule."))
                    # A confirmed *goal* does not automatically approve a new
                    # implementation mechanism; require an exact source claim.
                    if item.get("text") not in claims.values():
                        errors.append(_issue("UNSUPPORTED_REQUIRED_RULE", loc, "Mandatory dependency or business rule needs an exact pinned source claim."))
        return errors

    def validate(self, source_id: str, source_sha256: str, candidate: Any) -> dict[str, Any]:
        snapshot, errors = self._load_snapshot(source_id, source_sha256)
        if snapshot is not None:
            errors.extend(self._validate_candidate(candidate, snapshot))
        return {
            "status": "BLOCKED" if errors else "READY_DRAFT_ONLY",
            "valid": not errors,
            "source_id": source_id,
            "source_sha256": source_sha256,
            "candidate_digest": _digest_candidate(candidate),
            "findings": errors,
            "authority": "none-issued; approval source is source-reported and NOT independently verified",
            "effects": "read-only; no Issue filing, Task dispatch, Merge, Release, or Plugin update",
        }

    def render(self, source_id: str, source_sha256: str, candidate: Any) -> dict[str, Any]:
        verdict = self.validate(source_id, source_sha256, candidate)
        if not verdict["valid"]:
            return {**verdict, "markdown": None, "markdown_sha256": None}
        snapshot, _ = self._load_snapshot(source_id, source_sha256)
        assert snapshot is not None
        c = candidate
        lines = [
            f"# {c['id']}/{c['revision']} — {_md(c['title'])}", "",
            "## Provenance and drafting authority", "",
            f"- Source: `{_md(source_id)}` (SHA-256 `{source_sha256}`)",
            f"- Original goal: {_md(snapshot['original_goal'])}",
            f"- Approval provenance: {_md(snapshot['approval_provenance'])} (source-reported; NOT independently verified)",
            "- Current authorized scope in this prototype: **draft-only**. Not a permission receipt.",
            "- GitHub filing: **not-filed**. KAGARI/Task: **not-dispatched**.", "",
            "## Desired outcome and scenario", "",
            f"- Outcome: {_md(c['desired_outcome'])}",
            f"- Scenario: {_md(c['scenario'])}", "",
            "## Scope (candidate-proposed, not an additional approval)", "",
            "### In", "",
            *[f"- {_md(x)}" for x in c["in_scope"]], "",
            "### Candidate-only exclusions (not source-confirmed unless separately verified)", "",
            *([f"- {_md(x)}" for x in c["candidate_exclusions"]] or ["- none stated"]), "",
            "### Project-wide confirmed non-goals (as reported by pinned source)", "",
            *[f"- {_md(x)}" for x in snapshot["project_non_goals"]], "",
            "## Acceptance criteria", "",
            "| AC ID | State | Criterion | Source / Human decision |", "| --- | --- | --- | --- |",
        ]
        for ac in c["acceptance_criteria"]:
            provenance = (f"source claim `{ac['source_claim_id']}` (exact-match; semantic source not independently audited)"
                          if ac["status"] == "confirmed" else
                          f"Human decision `{ac['decision_id']}` required; NOT approved or binding")
            lines.append(f"| `{ac['id']}` | **{ac['status']}** | {_md(ac['text'])} | {provenance} |")
        lines.extend(["", "## Open Human decisions", ""])
        for decision in snapshot["human_decisions"]:
            lines.append(f"- `{decision['id']}`: {_md(decision['question'])} — Impact: {_md(decision['impact'])} (Human-owned; open)")
        lines.extend(["", "## Dependencies", ""])
        for dep in c["dependencies"]:
            lines.append(f"- [{dep['binding']}] {_md(dep['text'])} (AC: {', '.join('`'+x+'`' for x in dep['ac_refs'])})"
                         + ("; Human confirmation required before binding" if dep["binding"] == "conditional" else ""))
        if not c["dependencies"]:
            lines.append("- none declared")
        lines.extend(["", "## Business-rule revalidation (NOT Human execution authorization)", ""])
        for rule in c["business_revalidations"]:
            lines.append(f"- [{rule['binding']}] {_md(rule['text'])} (AC: {', '.join('`'+x+'`' for x in rule['ac_refs'])})"
                         + ("; proposed only, Human decision outstanding" if rule["binding"] == "conditional" else ""))
        if not c["business_revalidations"]:
            lines.append("- none declared")
        lines.extend(["", "## Authority revalidation — per-action execution STOP", "",
                      "The following statuses do not grant authority. Even an action absent from the source's explicit prohibition is UNKNOWN, not allowed.", "",
                      "| Action | Current state | Clearing authority and prerequisite | Revalidate immediately before this action |",
                      "| --- | --- | --- | --- |"])
        for action in ACTIONS:
            state = "STOP (explicitly prohibited)" if action in snapshot["prohibited_actions"] else "UNKNOWN (not authorized)"
            lines.append(f"| `{action}` | **{state}** | Human; separate approval for this exact operation/target | "
                         "pinned source snapshot, target revision, exact Human action approval, open decisions; if unknown, remain stopped |")
        lines.extend(["", "- Required revalidation fields: " + ", ".join(f"`{x}`" for x in REQUIRED_REVALIDATION) + ".",
                      "- Fallback: retain or amend the text draft within approved drafting scope only.",
                      "- Approval cannot be inferred from a design brief, a different operation, or this harness result.", "",
                      "## Candidate-proposed verification ideas (non-binding)", "",
                      "These model-authored suggestions are not accepted requirements or test gates. "
                      "Even imperative wording below cannot add an AC, require an implementation "
                      "mechanism, or turn a derived-unconfirmed AC into a required condition. "
                      "Only typed confirmed ACs or later explicitly approved revisions can bind acceptance.", "",
                      *[f"- **Proposed only (not an AC or a required test):** {_md(x)}" for x in c["evidence"]], "",
                      "## Handoff status", "",
                      "**DRAFT_ONLY / not-filed / not-dispatched**. Original-goal semantic equivalence and actual Human approval remain outside this mechanical test.", ""])
        markdown = "\n".join(lines)
        return {**verdict, "markdown": markdown,
                "markdown_sha256": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
                "action_revalidation_coverage": list(ACTIONS),
                "semantic_approval_verified": False}
