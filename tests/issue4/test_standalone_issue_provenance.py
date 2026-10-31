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


# Test-only mechanical probes for the exact R2 contract failures. These are
# intentionally *not* a live normal-Chat hook or a semantic approval verifier.
R2_PROJECT_NON_GOALS = ("予約取消", "通知", "外部カレンダー連携", "管理者操作", "課金")
R2_STOPPED_ACTIONS = (
    "GitHub Issue起票", "Task起動", "コード変更", "Merge", "Release", "Plugin更新",
)


def r2_detached_contract_gaps(
    body: str,
    *,
    approved_source: str = "BP-NC-ROOM-01/r1",
    non_goals: tuple[str, ...] = R2_PROJECT_NON_GOALS,
    stopped_actions: tuple[str, ...] = R2_STOPPED_ACTIONS,
    ac_status: tuple[str, str] = ("AC-002-04", "derived-unconfirmed"),
) -> set[str]:
    """Detect missing local fields in a deliberately normalized R2 fixture.

    Shared introduction/footer text must not satisfy a detached DES. Do not
    equate lexical checks here with actual runtime/semantic enforcement.
    """
    section = body.split("Standalone handoff\n", 1)
    if len(section) != 2:
        return {"standalone-section"}
    local = section[1]
    gaps = set()
    mandatory = {
        "source": f"Source: {approved_source}",
        "approval": "Approval scope: 仕様案作成のみ",
        "non-goals-section": "Project non-goals:",
        "human": "Human判断:",
        "action-gates-section": "Action gates:",
        "clearing": "Human解除:",
        "revalidation": "実行直前再照合:",
    }
    for field, value in mandatory.items():
        if value not in local:
            gaps.add(field)
    if "Project non-goals:" in local:
        non_goal_section = local.split("Project non-goals:", 1)[1].split("\n", 1)[0]
        for goal in non_goals:
            if goal not in non_goal_section:
                gaps.add(f"non-goal:{goal}")
    if "Action gates:" in local:
        gate_section = local.split("Action gates:", 1)[1].split("\n", 1)[0]
        for action in stopped_actions:
            if f"{action}=stop" not in gate_section:
                gaps.add(f"action:{action}")
    ac_id, status = ac_status
    if f"{ac_id} | {status} |" not in body:
        gaps.add(f"ac:{ac_id}:{status}")
    return gaps


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

    @staticmethod
    def r2_valid_detached() -> str:
        """Synthetic self-contained Issue that survives losing its parent."""
        non_goals = "、".join(R2_PROJECT_NON_GOALS)
        stops = "; ".join(f"{action}=stop" for action in R2_STOPPED_ACTIONS)
        return (
            "## DES-002\n"
            "Scenario: a booking list on mobile Web.\n"
            "AC-002-04 | derived-unconfirmed | Display detail; Human approval pending.\n"
            "Standalone handoff\n"
            "Source: BP-NC-ROOM-01/r1 (approved original goal).\n"
            "Approval scope: 仕様案作成のみ, not authority to file.\n"
            f"Project non-goals: {non_goals}\n"
            "Human判断: list visibility and display fields remain open.\n"
            f"Action gates: {stops}\n"
            "Human解除: separate approval for each affected action by Human.\n"
            "実行直前再照合: reread brief, current approval and unresolved decisions.\n"
        )

    def test_r4_blueprint_requires_local_non_goals_and_action_gates(self):
        text = read_contract(BLUEPRINT)
        for phrase in (
            "Standalone handoff",
            "project-wide non-goals in each candidate",
            "all five",
            "Action gates",
            "Plugin update",
            "Detached-body preflight",
            "bare `Derived` label",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_r4_issue_filer_checks_detached_body_before_text_handoff(self):
        text = read_contract(ISSUE_FILER)
        for phrase in (
            "Detached-body completeness gate",
            "even for a text-only Issue Filer handoff",
            "A shared project non-goal list is not sufficient",
            "bare `Derived` label",
            "Human clearing authority",
            "if still incomplete",
            "not-filed",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_r4_normalchat_r2_c02_parent_only_non_goals_fail(self):
        detached = self.r2_valid_detached().replace(
            "Project non-goals: " + "、".join(R2_PROJECT_NON_GOALS),
            "Project non-goals: unknown",
        )
        full = "## Shared\nProject non-goals: " + "、".join(R2_PROJECT_NON_GOALS) + "\n" + detached + "## DES-003\n..."
        isolated = extracted_issue(full, "DES-002")
        gaps = r2_detached_contract_gaps(isolated)
        self.assertEqual(
            {f"non-goal:{item}" for item in R2_PROJECT_NON_GOALS},
            {gap for gap in gaps if gap.startswith("non-goal:")},
        )
        self.assertIn("Project non-goals: 予約取消", full)

    def test_r4_normalchat_r2_c03_derived_without_local_qualifier_fails(self):
        detached = self.r2_valid_detached().replace(
            "AC-002-04 | derived-unconfirmed |", "AC-002-04 | Derived |"
        )
        full = "## Shared\nThe derived AC is not approved.\n" + detached + "## DES-003\n..."
        gaps = r2_detached_contract_gaps(extracted_issue(full, "DES-002"))
        self.assertIn("ac:AC-002-04:derived-unconfirmed", gaps)
        self.assertNotIn("source", gaps)

    def test_r4_normalchat_r2_shared_stop_does_not_clear_candidate(self):
        detached = self.r2_valid_detached().replace(
            "Action gates: " + "; ".join(f"{a}=stop" for a in R2_STOPPED_ACTIONS),
            "Action gates: GitHub Issue起票=stop",
        ).replace(
            "Human解除: separate approval for each affected action by Human.\n",
            "",
        ).replace(
            "実行直前再照合: reread brief, current approval and unresolved decisions.\n",
            "",
        )
        full = (
            "## Shared\nTask起動=stop; コード変更=stop; Merge=stop; "
            "Release=stop; Plugin更新=stop; Human解除 and execution-time checks.\n"
            + detached + "## DES-003\n..."
        )
        gaps = r2_detached_contract_gaps(extracted_issue(full, "DES-002"))
        for item in ("action:Task起動", "action:コード変更", "action:Merge",
                     "action:Release", "action:Plugin更新", "clearing", "revalidation"):
            with self.subTest(item=item):
                self.assertIn(item, gaps)

    def test_r4_all_current_action_gates_and_non_goals_survive_detach(self):
        full = (
            "## Shared\nThe global summary might be missing.\n"
            + self.r2_valid_detached() + "## DES-003\nNext candidate.\n"
        )
        isolated = extracted_issue(full, "DES-002")
        self.assertEqual(set(), r2_detached_contract_gaps(isolated))

    def test_r4_unverified_source_and_missing_non_goals_not_fabricated(self):
        """The checker must not invent business exclusions absent from input."""
        detached = self.r2_valid_detached().replace(
            "Project non-goals: " + "、".join(R2_PROJECT_NON_GOALS),
            "Project non-goals: unknown (not stated in source)",
        )
        self.assertEqual(
            set(),
            r2_detached_contract_gaps(detached, non_goals=()),
        )

    def test_r4_action_gate_is_not_business_non_goal(self):
        text = read_contract(BLUEPRINT) + read_contract(ISSUE_FILER)
        self.assertIn("temporary no-write test restriction", text)
        self.assertIn("temporary test-run restrictions", text)
        self.assertIn("never by itself authorizes filing", text)


if __name__ == "__main__":
    unittest.main()
