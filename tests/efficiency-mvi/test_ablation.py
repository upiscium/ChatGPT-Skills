"""Offline tests for the read-only ablation receipt summary."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

modpath = Path(__file__).with_name("ablation.py")
spec = importlib.util.spec_from_file_location("ablation", modpath)
ablation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ablation)


def run(condition="A", **changes):
    result = {
        "case_id": "T1", "trial": 1, "condition": condition, "history": "fresh",
        "memory": "unknown", "model": "fixed-model", "snapshot": "fixture-r1",
        "toolset": "same-common-tools", "outcome": "unknown",
        "evidence_ref": None, "tool_calls": None, "skill_bytes": None,
        "tokens": None, "unnecessary_asks": None, "duplicate_writes": None,
        "plugin_observed": None
    }
    result.update(changes)
    return result


class AblationTests(unittest.TestCase):
    def test_no_evidence_is_not_zero_effect(self):
        self.assertEqual(ablation.aggregate([])["status"], "no_evidence")

    def test_unknown_outcomes_do_not_count_as_pass(self):
        result = ablation.aggregate([run("A"), run("B")])
        self.assertEqual(result["status"], "no_scored_pairs")
        self.assertIsNone(result["comparisons"]["B-A"]["mean_pass_rate_delta"])
        self.assertIsNone(result["comparisons"]["B-A"]["metrics"]["tokens"]["mean_delta"])

    def test_pair_cost_and_pass_delta(self):
        result = ablation.aggregate([
            run("A", outcome="fail", evidence_ref="fixture expected status",
                tool_calls=2, tokens=150),
            run("B", outcome="pass", evidence_ref="fixture expected status",
                tool_calls=4, tokens=120)
        ])
        pair = result["comparisons"]["B-A"]
        self.assertEqual(pair["matched"], 1)
        self.assertEqual(pair["scored"], 1)
        self.assertEqual(pair["mean_pass_rate_delta"], 1)
        self.assertEqual(pair["metrics"]["tool_calls"]["mean_delta"], 2)
        self.assertEqual(pair["metrics"]["tokens"]["mean_delta"], -30)

    def test_memory_mismatch_must_not_pair(self):
        x = ablation.aggregate([run("A", memory="disabled"),
                               run("B", memory="enabled")])
        self.assertEqual(x["comparisons"]["B-A"]["matched"], 0)

    def test_missing_evidence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "evidence_ref"):
            ablation.aggregate([run(outcome="pass")])

    def test_unknown_tokens_are_not_estimated(self):
        x = ablation.aggregate([run("A", tool_calls=1), run("B", tool_calls=2)])
        self.assertIsNone(x["comparisons"]["B-A"]["metrics"]["tokens"]["mean_delta"])

    def test_condition_c_must_be_proved(self):
        with self.assertRaisesRegex(ValueError, "independent verification"):
            ablation.aggregate([run("C")])
        x = ablation.aggregate([run("C", plugin_unavailable_verified=True)])
        self.assertEqual(x["runs"], 1)

    def test_duplicate_record_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate condition"):
            ablation.aggregate([run(), run()])

    def test_boolean_is_not_an_integer_measure(self):
        with self.assertRaisesRegex(ValueError, "tool_calls"):
            ablation.aggregate([run(tool_calls=True)])

    def test_jsonl_blank_lines(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "r.jsonl"
            path.write_text(json.dumps(run()) + "\n\n", encoding="utf-8")
            self.assertEqual(len(ablation.load(path)), 1)


if __name__ == "__main__":
    unittest.main()
