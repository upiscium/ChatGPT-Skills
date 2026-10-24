"""Read-only aggregation of independently collected Plugin ablation receipts.

Usage: python3 tests/efficiency-mvi/ablation.py path/to/runs.jsonl

This tool cannot determine whether the model actually used the Plugin,
what Memory it saw, or whether a human-scored outcome is correct.
It never sends prompts or writes files.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from statistics import mean
import sys

CONDITIONS = {"A", "B", "C"}
COUNTS = ("tool_calls", "skill_bytes", "tokens", "unnecessary_asks",
          "duplicate_writes")
COMMON = ("case_id", "trial", "history", "memory", "model", "snapshot", "toolset")


def validate(row: dict) -> None:
    if not isinstance(row, dict):
        raise ValueError("each receipt must be an object")
    for field in COMMON + ("condition", "outcome", "evidence_ref"):
        if field not in row:
            raise ValueError("missing field: " + field)
    for field in ("case_id", "model", "snapshot", "toolset"):
        if not isinstance(row[field], str) or not row[field].strip():
            raise ValueError("invalid field: " + field)
    if not isinstance(row["trial"], int) or isinstance(row["trial"], bool) or row["trial"] < 1:
        raise ValueError("trial must be a positive integer")
    if row["history"] not in ("fresh", "continued"):
        raise ValueError("invalid history")
    if row["memory"] not in ("enabled", "disabled", "unknown"):
        raise ValueError("invalid memory")
    if row["condition"] not in CONDITIONS:
        raise ValueError("invalid condition")
    if row["outcome"] not in ("pass", "fail", "unknown"):
        raise ValueError("invalid outcome")
    if row["outcome"] != "unknown" and (
        not isinstance(row["evidence_ref"], str) or not row["evidence_ref"].strip()
    ):
        raise ValueError("a pass/fail requires a nonempty evidence_ref")
    for name in COUNTS:
        value = row.get(name)
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 0
        ):
            raise ValueError(name + " must be a nonnegative integer or null")
    if row.get("plugin_observed") not in (None, True, False):
        raise ValueError("plugin_observed must be boolean or null")
    if row["condition"] == "C" and row.get("plugin_unavailable_verified") is not True:
        raise ValueError("C requires independent verification of unavailability")


def key(row: dict) -> tuple:
    return tuple(row[f] for f in COMMON)


def aggregate(rows: list[dict]) -> dict:
    if not rows:
        return {"status": "no_evidence", "runs": 0, "comparisons": {}}
    buckets = defaultdict(dict)
    for row in rows:
        validate(row)
        group = buckets[key(row)]
        if row["condition"] in group:
            raise ValueError("duplicate condition for the same matched trial")
        group[row["condition"]] = row

    # Matching within a trial is not enough: a single mean must not pool
    # distinct cases, Memory regimes, models, fixtures or toolsets.
    matched_strata = set()
    for group in buckets.values():
        if "B" in group and ("A" in group or "C" in group):
            matched_strata.add(tuple(group["B"][f] for f in COMMON if f != "trial"))
    if len(matched_strata) > 1:
        raise ValueError("mixed comparison strata; summarize each case, history, "
                         "Memory state, model, snapshot and toolset separately")

    comparisons = {}
    for label, before, after in (("B-A", "A", "B"), ("C-B", "B", "C")):
        matched = [(v[before], v[after]) for v in buckets.values()
                   if before in v and after in v]
        valid = [(a, b) for a, b in matched
                 if a["outcome"] != "unknown" and b["outcome"] != "unknown"]
        delta_pass = (mean(int(b["outcome"] == "pass") -
                           int(a["outcome"] == "pass") for a, b in valid)
                      if valid else None)
        metrics = {}
        for metric in COUNTS:
            observed = [(a[metric], b[metric]) for a, b in matched
                        if a.get(metric) is not None and b.get(metric) is not None]
            metrics[metric] = {"paired": len(observed),
                               "mean_delta": mean(b - a for a, b in observed)
                               if observed else None}
        comparisons[label] = {
            "matched": len(matched), "scored": len(valid),
            "mean_pass_rate_delta": delta_pass, "metrics": metrics
        }

    return {
        "status": "descriptive" if any(
            v["scored"] or any(m["paired"] for m in v["metrics"].values())
            for v in comparisons.values()) else "no_scored_pairs",
        "runs": len(rows),
        "unknown_outcomes": sum(r["outcome"] == "unknown" for r in rows),
        "comparisons": comparisons,
        "limitations": ("A is not necessarily Plugin-off; Memory causality "
                        "and actual token usage cannot be inferred from this file.")
    }


def load(path: Path) -> list[dict]:
    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
            validate(parsed)
        except ValueError as exc:
            raise ValueError(f"line {line_no}: {exc}") from exc
        records.append(parsed)
    return records


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: ablation.py <runs.jsonl>")
    try:
        print(json.dumps(aggregate(load(Path(sys.argv[1]))),
                         ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
