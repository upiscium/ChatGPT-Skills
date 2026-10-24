"""Static guardrails for the lean-context and MVI-first policy.

These checks verify documented operating rules, not actual LLM behavior.
Measure context usage and human-Ask outcomes with scenarios.md.
Run: python3 -m unittest discover -s tests/efficiency-mvi -p 'test_*.py'
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def skill(rel):
    return (ROOT / "skills" / rel).read_text(encoding="utf-8")


class ArcaPolicyContractTests(unittest.TestCase):
    def test_no_checkpoint_for_identical_status(self):
        handoff = skill("repo-handoff/SKILL.md")
        status = skill("repo-status/SKILL.md")
        self.assertIn("Do **not** write a fresh marker for unchanged reads", handoff)
        self.assertIn("Repeated read-only status with no new state", status)
        self.assertNotIn("For every repository-workflow response that observes or changes state", handoff)

    def test_dispatch_and_external_authority_not_weakened(self):
        loop = skill("dev-loop/SKILL.md")
        handoff = skill("repo-handoff/SKILL.md")
        self.assertIn("Always save/read back dispatch intent before sending", loop)
        self.assertIn("dispatch-intent recording **before** send", handoff)
        self.assertIn("never disclose secrets", loop)
        self.assertIn("silently merge or release", loop)
        self.assertIn("material change to the accepted threat model remains human-owned", loop)

    def test_context_budget_and_lazy_references(self):
        loop = skill("dev-loop/SKILL.md")
        plan = skill("patch-plan/SKILL.md")
        self.assertIn("Reuse previously loaded Skill instructions and verified state", loop)
        self.assertIn("Limit each tool response to pertinent fields", loop)
        self.assertIn("Use the relevant sections of", plan)
        self.assertIn("only when producing an execution-ready plan", plan)

    def test_mvi_risk_is_scoped_not_ignored(self):
        plan = skill("patch-plan/SKILL.md")
        review = skill("change-review/SKILL.md")
        security = skill("security-audit/SKILL.md")
        human = skill("human-review/SKILL.md")
        self.assertIn("production-deferred", plan)
        self.assertIn("Only in-scope failures block the MVI", plan)
        self.assertIn("approved stage and actually reachable effects", review)
        self.assertIn("do not automatically convert (b) or (c)", security)
        self.assertIn("Missing threat-model evidence is", security)
        self.assertIn("Preserve explicit material risk", human)

    def test_sweep_avoids_extra_tool_work(self):
        sweep = skill("human-review/references/decision-sweep.md")
        self.assertIn("Do not fetch or re-read supporting Skills", sweep)
        self.assertIn("material changes to approved risk are human-owned", sweep)


if __name__ == "__main__":
    unittest.main()
