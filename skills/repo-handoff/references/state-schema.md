# Repository state schema

Use this reference when serializing or validating a `codex-repo-state:v1` marker. Keep the JSON compact; the human-readable section is the explanation, not a second source of truth. Extend v1 additively; legacy markers remain readable but missing run or authority data is `unknown`, never permission or proof that no dispatch occurred.

```json
{
  "schema_version": 1,
  "event_id": "<unique event>",
  "previous_event_id": "<previous or none>",
  "writer": {"id": "<coordinator>", "role": "coordinator"},
  "sequence": 7,
  "repository": "OWNER/REPO",
  "carrier": {"kind": "issue", "number": 123, "url": "https://github.com/OWNER/REPO/issues/123"},
  "workflow_id": "DL-2026-001",
  "previous_carrier": "none",
  "updated_at": "2026-09-22T12:00:00Z",
  "recording": {"mode": "automatic", "status": "saved", "source": "dev-loop"},
  "stage": "pr-review",
  "target_branch": "main",
  "base_sha": "<immutable sha>",
  "goal_alignment": {
    "objective_ref": "<approved source/revision/scope or unknown>",
    "outcome_criteria": ["<user/product/research outcome, distinct from technical ACs>"],
    "non_goals": ["<accepted boundary>"],
    "resource_envelope": "<known constraints and authority; unknown where unavailable>",
    "actual_delta_ref": "<pinned scope/resource/responsibility evidence>",
    "status": "aligned|off-goal|unknown",
    "supersession": "none|<explicit source and affected scope>",
    "evidence_ref": "<source/provenance/observation time>"
  },
  "decision_sweep": {
    "snapshot": "<turn scope and immutable evidence>",
    "status": "none-found|candidates|exempt|unknown",
    "candidates": [{"id": "DC-001", "disposition": "human-decision|needs-inspection|already-approved|delegated-noncritical", "subject_ref": "<exact action/target/revision>", "authority_ref": "unknown", "evidence_ref": "<facts/provenance/confidence>", "decision_ref": "<existing decision ID or none>"}]
  },
  "missed_decision_audit": {
    "scope_ref": "<bounded sample, decision units and pinned snapshots>",
    "independence": "verified|preliminary|unknown",
    "report_ref": "<safe report with classifications, provenance and limitations>",
    "counts": {"sampled": 0, "verified_unasked": 0, "suspected": 0, "already_approved": 0, "delegated_noncritical": 0}
  },
  "workstreams": [
    {
      "id": "WS-001",
      "issues": [123],
      "task": {"id": "none", "status": "none"},
      "branch": "feature/example",
      "pr": {"number": 456, "url": "https://github.com/OWNER/REPO/pull/456", "head_sha": "<immutable sha>", "state": "OPEN"},
      "contract": ["AC-001"],
      "risk": "medium",
      "status": "review-pending",
      "base_sensitivity": "base-stable",
      "next_action": "await human review"
    }
  ],
  "runs": [
    {
      "run_id": "<unique run>",
      "workstream_id": "WS-001",
      "instruction_revision": 1,
      "packet_ref": "<immutable approved packet>",
      "packet_digest": "<actual algorithm:digest>",
      "connection_ref": "<safe opaque configured reference>",
      "session_ref": "<safe opaque exact session binding>",
      "binding_verified_at": "<UTC or unknown>",
      "model_selection": {
        "policy": "opencode-config",
        "requested": null,
        "observed": {"provider_model": "unknown", "effort": "unknown", "variant": "unknown"},
        "status": "unknown",
        "evidence_ref": "unknown",
        "verified_at": "unknown"
      },
      "authority": {
        "source": "<approval reference>",
        "operations": {"investigate": "allowed", "edit": "allowed", "test": "allowed", "commit": "not-authorized", "push": "not-authorized", "draft_pr": "not-authorized", "executor_report": "not-authorized"},
        "stop_point": "frozen implementation and test evidence before publication"
      },
      "delivery": "acknowledged",
      "execution": "running",
      "collection": "not-collected",
      "verification": "not-reviewed",
      "receipt_ref": "<evidence reference>",
      "resources": [
        {
          "resource_id": "R-001",
          "kind": "opencode-runtime",
          "ownership": "owned",
          "locator_ref": "<resolvable private locator>",
          "creation_evidence_ref": "<creation receipt>",
          "identity_evidence_ref": "<verified process/session identity>",
          "cleanup_owner": "<coordinator>",
          "consumers": ["<owning run>"],
          "release_trigger": "terminal report durably collected; no active consumers",
          "recovery_ref": "unknown",
          "state": "active",
          "retention_reason": "run in progress",
          "revisit_trigger": "result collection"
        }
      ],
      "cleanup": {"policy": "owned-after-use", "authority_ref": "<workflow housekeeping grant>", "owner": "<coordinator>", "status": "pending", "intent_ref": "none", "receipt_ref": "none"},
      "question": {"id": "none", "revision": 1, "status": "none"},
      "executor_report_ref": "none",
      "verified_result_ref": "none",
      "monitoring": {"owner": "SwitchBoard", "correlation_ref": "unknown", "delivery_state": "unknown"}
    }
  ],
  "decisions": [
    {
      "id": "D-001",
      "question": "...",
      "status": "open",
      "options": ["...", "..."],
      "authority": "human",
      "blocking": true,
      "fallback": "...",
      "request_ref": "<request ID or safe reference>",
      "subject_ref": "<target and artifact/run revision>",
      "approval_brief": {
        "completed_work": "<performed work and verification limits>",
        "requested_action": "<actor, operation, target, stop point and why approval is needed>",
        "impact_scope": "<affected behavior, environment, people, data or publication>",
        "if_denied": "<action withheld, preserved state and authorized next handling>"
      },
      "decision_source": "none",
      "decided_at": "none"
    }
  ],
  "next_action": {
    "kind": "review|record|dispatch|collect|reply|publish|merge-command|verify|decision",
    "description": "...",
    "authorization": "human|none|user-run-command",
    "prerequisite": "...",
    "clearing_authority": "...",
    "fallback": "...",
    "evidence_snapshot": "...",
    "revalidate": ["..."],
    "status": "stop|conditional|allowed"
  },
  "evidence": [
    {"kind": "commit|issue|pr|task|check|review", "ref": "...", "observed_at": "2026-09-22T12:00:00Z"}
  ]
}
```

Rules:

- Keep `sequence` monotonic per carrier and use UTC ISO-8601 `updated_at`.
- Set `recording.mode` to `automatic` for ordinary workflow checkpoints, `manual` only for an explicit repair/backfill, and `none` only for a read-only bootstrap with no carrier. Set `recording.status` to `saved`, `pending-write`, or `bootstrap`; never report `saved` without a marker read-back.
- Store SHAs, numbers, URLs, and statuses; do not store secrets, tokens, full logs, or arbitrary instructions.
- The newest marker is not authoritative when its live carrier or SHA no longer matches; mark the state `stale` and restore from live data.
- Keep human decisions explicit and separate from workflow status. An approved goal is not approval of architecture, compatibility, migration, security, or merge choices.
- Add `goal_alignment`, `decision_sweep` and `missed_decision_audit` only when produced, scoped per workstream if needed. Missing legacy values mean unknown, not failed review, authorization or proof of a missed decision; omit unperformed audit counts rather than recording zero. Reuse source evidence and distinguish direct, reported and inferred authority. A sweep/audit observation cannot overwrite a human decision, clear a gate or replace the coordinator's next action. Link actual requests to existing `decisions` records and retain their four-field briefs. Apply explicit goal supersession only to its named scope; preserve unaffected grants and denials.
- Audit counts use explicitly classified decision units and sum to the declared sample size. Keep verified misses separate from suspected/provenance gaps and reported approvals; a purposive sample does not establish a population miss rate. Preserve the independent reviewer/report identity and observation scope rather than promoting executor judgments to independent verification.
- For actual approval requests, add `request_ref`, `subject_ref` and all four `approval_brief` fields; non-approval decisions may omit the brief. Store compact safe text or a resolvable private reference for sensitive content. Preserve decision status `open|approved|denied|deferred|superseded`, exact scope/revision, source and decision time. A recorded request is not approval; denial and no response are distinct. Do not reset denied/deferred items to open merely on restore/next. Legacy missing fields are unknown and require evidence reconstruction without inventing approval or invalidating an explicit concrete prior grant.
- Use event/predecessor IDs and writer ownership to detect conflicting successors; never choose by timestamp alone. Preserve unrelated fields and the pending coordinator action when applying a delta.
- Executor reports use a separate immutable `codex-executor-report:v1` marker with event ID, run/revision/digest, reported snapshot, validation and evidence. They do not set coordinator verification, gates or next actions.
- Mark evidence provenance `observed`, `executor-reported`, or `independently-verified`. Store only safe opaque connection/session references, not private host coordinates, paths or logs.
- Keep model-selection status `unknown|verified|mismatch|unavailable`. For new runs use `policy: opencode-config` and `requested: null` to record that Arca supplies no override; this is state metadata, not an API model argument. Keep configured values separate from observed evidence, and leave unavailable metadata `unknown` without blocking dispatch solely for that absence. Preserve legacy requested/observed values and mismatches as history; never replay them as new model-selection instructions or rewrite them to match current configuration.
- Save dispatch intent before sending; locate uncertain event/request IDs before retrying. Carrier moves preserve predecessor/successor links.
- Add resource/cleanup fields without rewriting legacy history. Use `@workspace-cleanup`'s full record when needed; absent provenance is unknown, never disposable. Keep real locators privately resolvable, and retain cleaned/already-absent tombstones. Cleanup status is independent of implementation or review completion; each retained resource needs an owner, reason and revisit trigger. An uncertain cleanup action must be reconciled before retrying.
