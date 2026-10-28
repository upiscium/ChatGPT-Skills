"""Issue #9: safe offline validation of KAGARI-owned Session API evidence."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "skills/opencode-bridge/scripts/observe-session.py"
SID = "ses_fixtureA1"


class SessionReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="arca9-observation-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.work = root / "work"
        self.work.mkdir()
        self.evidence_file = root / "native-session-evidence.json"
        self.snapshot = {
            "schema": "kagari-opencode-observation-v1",
            "health": {"healthy": True},
            "session": {"id": SID, "title": "issue9-review-task",
                        "agent": "reviewer", "directory": str(self.work)},
            "statuses": {},  # OpenCode 1.18.35 omits *idle* Sessions.
            "messages": [{
                "info": {"role": "assistant", "agent": "reviewer",
                         "sessionID": SID,
                         "providerID": "openai", "modelID": "fixture-model",
                         "finish": "stop"},
                "parts": [{"type": "text", "text": "PRIVATE_CONTENT"}],
            }],
            "permissions": [], "questions": [],
        }

    def call(self):
        if not self.evidence_file.exists():
            self.evidence_file.write_text(json.dumps(self.snapshot))
            self.evidence_file.chmod(0o600)
        args = [sys.executable, str(VALIDATOR),
                "--observation-id", "local-observation-A1",
                "--session-id", SID,
                "--directory", str(self.work),
                "--expected-title", "issue9-review-task",
                "--agent", "reviewer",
                "--evidence-file", str(self.evidence_file)]
        done = subprocess.run(args, capture_output=True, text=True, timeout=4,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(len(done.stdout.splitlines()), 1, done.stderr)
        return done.returncode, json.loads(done.stdout)

    def test_complete_observation_never_implies_task_binding_or_authenticity(self):
        code, value = self.call()
        self.assertEqual(code, 0)
        self.assertEqual(value["status"], "completed")
        self.assertEqual(value["evidence"],
                         ["opencode_initialized", "session_created", "model_started",
                          "completed"])
        self.assertEqual(value["model_observed"], "openai/fixture-model")
        self.assertEqual(value["task_binding"], "not_verified_by_observer")
        self.assertEqual(value["source_authenticity"], "not_verified_by_observer")
        self.assertEqual(value["observation_id"], "local-observation-A1")
        self.assertNotIn("run_id", value)
        self.assertNotIn("PRIVATE_CONTENT", json.dumps(value))

    def test_busy_session_never_claims_completion(self):
        self.snapshot["statuses"][SID] = {"type": "busy"}
        code, value = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(value["status"], "running")
        self.assertNotIn("completed", value["evidence"])

    def test_missing_status_entry_means_idle_in_supported_opencode_api(self):
        self.assertEqual(self.snapshot["statuses"], {})
        code, value = self.call()
        self.assertEqual((code, value["status"]), (0, "completed"))

    def test_title_or_role_binding_conflict_is_rejected(self):
        for field, replacement in (("title", "another-task"), ("agent", "build"),
                                   ("directory", "/other/worktree"), ("id", "ses_other")):
            with self.subTest(field=field):
                self.snapshot["session"][field] = replacement
                code, result = self.call()
                self.assertEqual(code, 75)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["reason"], "session_binding_mismatch")
                self.snapshot["session"][field] = {
                    "title": "issue9-review-task", "agent": "reviewer",
                    "directory": str(self.work), "id": SID,
                }[field]
                self.evidence_file.unlink()

    def test_missing_native_session_agent_binds_from_assistant_metadata(self):
        # Some OpenCode responses omit the optional Session.agent field;
        # actual assistant metadata can still prove the exact role.
        self.snapshot["session"].pop("agent")
        code, result = self.call()
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["model_observed"], "openai/fixture-model")

    def test_missing_session_agent_without_assistant_evidence_is_unknown(self):
        self.snapshot["session"].pop("agent")
        self.snapshot["messages"] = []
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["reason"], "agent_not_observed")
        self.assertNotIn("completed", result["evidence"])

    def test_other_session_message_cannot_prove_this_session_complete(self):
        self.snapshot["messages"][0]["info"]["sessionID"] = "ses_unrelatedA1"
        code, receipt = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(receipt["status"], "unknown")
        self.assertNotIn("completed", receipt["evidence"])

    def test_missing_message_session_id_keeps_compatible_role_checks(self):
        # A source without optional Session metadata remains explicitly
        # unauthenticated; it must still pass assistant agent and role checks.
        self.snapshot["messages"][0]["info"].pop("sessionID")
        code, receipt = self.call()
        self.assertEqual(code, 0)
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["source_authenticity"],
                         "not_verified_by_observer")

    def test_invalid_payload_cannot_prove_model_started(self):
        self.snapshot["messages"][0]["parts"] = [{"type": "text"}]
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertNotIn("model_started", result["evidence"])

    def test_new_user_turn_after_terminal_cannot_be_complete(self):
        self.snapshot["messages"].append({
            "info": {"role": "user"},
            "parts": [{"type": "text", "text": "new question"}]})
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "unknown")

    def test_assistant_error_cannot_prove_completion(self):
        self.snapshot["messages"][0]["info"]["error"] = {"name": "FixtureError"}
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertNotIn("completed", result["evidence"])

    def test_native_question_is_never_answered(self):
        self.snapshot["questions"].append({"sessionID": SID, "id": "que_A1"})
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "awaiting_human")
        self.assertEqual(result["task_binding"], "not_verified_by_observer")

    def test_oversized_or_nonregular_evidence_fails_without_hang(self):
        self.evidence_file.write_bytes(b"X" * (1024 * 1024 + 1))
        self.evidence_file.chmod(0o600)
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "unknown")
        self.evidence_file.unlink()
        os.mkfifo(self.evidence_file, mode=0o600)
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "unknown")

    def test_public_or_linked_evidence_is_rejected(self):
        self.evidence_file.write_text(json.dumps(self.snapshot))
        self.evidence_file.chmod(0o644)
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "unknown")
        self.evidence_file.unlink()
        source = self.evidence_file.with_suffix(".source")
        source.write_text(json.dumps(self.snapshot))
        source.chmod(0o600)
        self.evidence_file.symlink_to(source)
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "unknown")

    def test_evidence_inside_product_worktree_is_not_read(self):
        self.evidence_file = self.work / "evidence.json"
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "unknown")

    def test_symlinked_parent_alias_cannot_hide_worktree_local_evidence(self):
        source = self.work / "evidence.json"
        source.write_text(json.dumps(self.snapshot))
        source.chmod(0o600)
        alias = Path(self.temp.name) / "work-alias"
        alias.symlink_to(self.work, target_is_directory=True)
        self.evidence_file = alias / source.name
        self.assertFalse(self.evidence_file.is_symlink())
        self.assertFalse(self.evidence_file.is_relative_to(self.work))
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "unknown")

    def test_parent_dotdot_alias_cannot_hide_worktree_local_evidence(self):
        source = self.work / "evidence.json"
        source.write_text(json.dumps(self.snapshot))
        source.chmod(0o600)
        outer = Path(self.temp.name) / "outer"
        outer.mkdir()
        self.evidence_file = outer / ".." / "work" / source.name
        self.assertFalse(self.evidence_file.is_relative_to(self.work))
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
