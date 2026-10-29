"""Source-only contract checks for Issue #4 standalone Issue handoff.

These tests exercise the written Skill requirements and illustrative text
extraction; they do not prove a model will comply in a live Work session.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT = ROOT / "skills/blueprint/SKILL.md"
ISSUE_FILER = ROOT / "skills/issue-filer/SKILL.md"


def read_contract(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extracted_issue(full_response: str, issue_id: str) -> str:
    """A loss-prone handoff that takes only one Issue heading and its body."""
    start = "## " + issue_id + "\n"
    return full_response.split(start, 1)[1].split("\n## ", 1)[0]


class StandaloneIssueProvenanceTests(unittest.TestCase):
    def test_blueprint_requires_standalone_goal_provenance(self):
        text = read_contract(BLUEPRINT)
        self.assertIn("self-contained when copied into a standalone Issue body", text)
        self.assertIn("original approved user goal/source/revision", text)
        self.assertIn("candidate body by itself", text)
        self.assertIn("without the parent brief", text)
        self.assertIn("own scope, ACs, dependencies and evidence", text)

    def test_blueprint_distinguishes_material_inferences(self):
        text = read_contract(BLUEPRINT)
        for phrase in (
            "material",
            "confirmed",
            "derived-unconfirmed",
            "proposed restriction is not an approved exclusion",
            "Human decision owner",
            "filing/dispatch/implementation status",
            "keep unrelated approved work moving",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_issue_filer_does_not_depend_on_parent_summary(self):
        text = read_contract(ISSUE_FILER)
        self.assertIn("### Standalone Issue provenance", text)
        self.assertIn("individual Issue body alone", text)
        self.assertIn("do not rely on shared introductory text", text)
        self.assertIn("the exact approval scope", text)
        self.assertIn("original approved user goal and source/revision", text)
        self.assertIn("observable AC IDs, dependencies and evidence", text)

    def test_issue_filer_preserves_unconfirmed_ac_out_dependency(self):
        text = read_contract(ISSUE_FILER)
        for phrase in (
            "material",
            "ACs, scope exclusions and inferred dependencies",
            "confirmed",
            "derived-unconfirmed",
            "inside this Issue body",
            "unapproved restriction",
            "confirmed Out",
            "unconditional implementation criterion",
            "after any extraction, deduplication or rewrite",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_issue_filer_has_stop_and_no_redundant_gate(self):
        text = read_contract(ISSUE_FILER)
        for phrase in (
            "return `not-filed`",
            "missing provenance/decision",
            "not a Human-approved condition",
            "do not manufacture approval",
            "request a second decision that was already granted",
            "Explicit Issue filing authority",
            "never implies implementation/Task authority",
            "stop or permitted fallback",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_blueprint_keeps_view_and_edit_permissions_separate(self):
        text = read_contract(BLUEPRINT)
        for phrase in (
            "original approved user-goal wording faithful",
            "permission to edit only one's own booking",
            "permission to view *only* one's own bookings",
            "mandatory owner-only filter",
            "unrestricted all-employee visibility",
            "default/fallback or acceptance/revalidation step",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_issue_filer_does_not_reconfirm_unapproved_scope_elsewhere(self):
        text = read_contract(ISSUE_FILER)
        for phrase in (
            "original approved goal",
            "mandatory dependency",
            "permitted implementation fallback",
            "revalidation check",
            "qualifier in one section cannot excuse",
            "owner-only edit does **not** authorize owner-only visibility",
            "stop the affected viewing-policy implementation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_issue_filing_remains_user_authorized(self):
        text = read_contract(ISSUE_FILER)
        self.assertIn("Do not create issues when the user asked only for review", text)
        self.assertIn("Search open and closed issues", text)
        self.assertIn("Issue filing permission does not grant Task execution", text)

    def test_reproduces_parent_qualifier_loss_from_work_issue(self):
        # Modeled on U2 Work DES-001: parent says unapproved, while Out looks final.
        work_output = (
            "## Shared human status\n"
            "List visibility is derived-unconfirmed; the Human has not approved it.\n"
            "## DES-001\n"
            "Original goal: BP-ROOM-MOBILE/r1\n"
            "Out: publication of other users' booking lists.\n"
            "AC-LIST-01: show user's own bookings.\n"
            "## DES-002\n"
            "Next feature.\n"
        )
        detached = extracted_issue(work_output, "DES-001")
        self.assertNotIn("derived-unconfirmed", detached)
        self.assertNotIn("Human has not approved", detached)
        self.assertIn("Out: publication of other users", detached)
        self.assertIn("derived-unconfirmed", work_output)

    def test_standalone_candidate_keeps_material_provenance_when_detached(self):
        safe_output = (
            "## Shared summary\n"
            "Parent text may be omitted.\n"
            "## DES-001\n"
            "Original approved goal/revision: BP-ROOM-MOBILE/r1; show existing bookings.\n"
            "Approval: draft specs only; no Issue filing or Task execution granted.\n"
            "AC-LIST-01 (confirmed): employees can select a booking from mobile Web.\n"
            "Out proposal (derived-unconfirmed): other users' lists hidden;\n"
            "  Human decision owner: User; view scope still open.\n"
            "Action stop: no Issue filing or Task execution until separately authorized;\n"
            "  unconfirmed restriction is not a binding implementation AC.\n"
            "## DES-002\n"
            "Next feature.\n"
        )
        detached = extracted_issue(safe_output, "DES-001")
        for phrase in (
            "Original approved goal/revision",
            "BP-ROOM-MOBILE/r1",
            "draft specs only",
            "AC-LIST-01 (confirmed)",
            "derived-unconfirmed",
            "Human decision owner: User",
            "view scope still open",
            "Action stop",
            "not a binding implementation AC",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, detached)


if __name__ == "__main__":
    unittest.main()
