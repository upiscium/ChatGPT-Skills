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
        "requested": {"name": "GPT-6.1 Sol", "provider_model": "openai/gpt-6.1-sol", "effort": "high", "variant": "high"},
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
      "fallback": "..."
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
- Use event/predecessor IDs and writer ownership to detect conflicting successors; never choose by timestamp alone. Preserve unrelated fields and the pending coordinator action when applying a delta.
- Executor reports use a separate immutable `codex-executor-report:v1` marker with event ID, run/revision/digest, reported snapshot, validation and evidence. They do not set coordinator verification, gates or next actions.
- Mark evidence provenance `observed`, `executor-reported`, or `independently-verified`. Store only safe opaque connection/session references, not private host coordinates, paths or logs.
- Keep model-selection status `unknown|verified|mismatch|unavailable`, with requested values distinct from observed evidence. Legacy runs without these fields have unknown selection. Do not rewrite historical observed settings to match a new preference or infer verification from requested flags.
- Save dispatch intent before sending; locate uncertain event/request IDs before retrying. Carrier moves preserve predecessor/successor links.
