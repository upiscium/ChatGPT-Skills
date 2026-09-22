# Repository state schema

Use this reference when serializing or validating a `codex-repo-state:v1` marker. Keep the JSON compact; the human-readable section is the explanation, not a second source of truth.

```json
{
  "schema_version": 1,
  "sequence": 7,
  "repository": "OWNER/REPO",
  "carrier": {"kind": "issue", "number": 123, "url": "https://github.com/OWNER/REPO/issues/123"},
  "workflow_id": "DL-2026-001",
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
    "kind": "review|record|implement|merge-command|verify|decision",
    "description": "...",
    "authorization": "human|none|user-run-command",
    "prerequisite": "...",
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
