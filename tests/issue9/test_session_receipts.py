"""Issue #9: source-only, bounded native Session API receipt regressions."""
from __future__ import annotations

import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[2]
OBSERVE = ROOT / "skills/opencode-bridge/scripts/observe-session.py"
SID = "ses_fixtureA1"


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        fixture = self.server.fixture
        name = urlsplit(self.path).path
        fixture["observed"].append(("GET", name,
                                    self.headers.get("Authorization"),
                                    parse_qs(urlsplit(self.path).query)))
        if name == "/global/health":
            result = fixture["health"]
        elif name == "/session/" + SID:
            result = fixture["session"]
        elif name == "/session/status":
            result = fixture["statuses"]
        elif name == "/session/" + SID + "/message":
            result = fixture["messages"]
        elif name == "/permission":
            result = fixture["permissions"]
        elif name == "/question":
            result = fixture["questions"]
        else:
            self.send_error(404)
            return
        if fixture.get("redirect") and name == "/global/health":
            self.send_response(302)
            self.send_header("Location", "http://example.invalid/credentials")
            self.end_headers()
            return
        body = json.dumps(result).encode()
        if fixture.get("oversize") and name == "/global/health":
            body = b" " * (1024 * 1024 + 10)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        return


class SessionReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="arca9-session-receipt-")
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.work = root / "work"
        self.work.mkdir()
        self.password = root / "server-secret"
        self.password.write_text("SYNTHETIC_PRIVATE_PASSWORD\n")
        self.password.chmod(0o600)
        message = {"info": {"role": "assistant", "agent": "reviewer",
                            "providerID": "openai", "modelID": "fake-model",
                            "finish": "stop"},
                   "parts": [{"type": "text", "text": "SENSITIVE_OUTPUT_FIXTURE"}]}
        self.fixture = {
            "health": {"healthy": True},
            "session": {"id": SID, "directory": str(self.work), "agent": "reviewer", "title": "issue9-review-task"},
            "statuses": {},
            "messages": [message],
            "permissions": [],
            "questions": [],
            "observed": [],
        }
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        self.server.fixture = self.fixture
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def call(self, *args):
        argv = [sys.executable, str(OBSERVE), "--run-id", "issue9-probe",
                "--session-id", SID, "--agent", "reviewer",
                "--expected-title", "issue9-review-task",
                "--directory", str(self.work),
                "--port", str(self.server.server_address[1]),
                "--password-file", str(self.password), *args]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        done = subprocess.run(argv, text=True, capture_output=True,
                              timeout=5, env=env)
        self.assertEqual(len(done.stdout.splitlines()), 1)
        return done.returncode, json.loads(done.stdout)

    def test_completed_requires_bound_session_model_and_terminal_evidence(self):
        code, receipt = self.call()
        self.assertEqual(code, 0)
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["evidence"],
                         ["opencode_initialized", "session_created", "model_started",
                          "completed"])
        self.assertEqual(receipt["model_observed"], "openai/fake-model")
        self.assertNotIn("SENSITIVE_OUTPUT_FIXTURE", json.dumps(receipt))
        self.assertNotIn("SYNTHETIC_PRIVATE_PASSWORD", json.dumps(receipt))
        self.assertEqual(len(self.fixture["observed"]), 6)
        self.assertTrue(all(method == "GET" for method, *_ in self.fixture["observed"]))
        self.assertTrue(all(params.get("directory") == [str(self.work)]
                            for _, _, _, params in self.fixture["observed"]))
        expected = "Basic " + base64.b64encode(b"opencode:SYNTHETIC_PRIVATE_PASSWORD").decode()
        self.assertTrue(all(auth == expected for _, _, auth, _ in self.fixture["observed"]))

    def test_inconsistent_role_or_worktree_is_blocked(self):
        self.fixture["session"]["agent"] = "build"
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "session_binding_mismatch")
        self.assertEqual(result["evidence"], ["opencode_initialized"])

    def test_session_title_mismatch_is_blocked(self):
        self.fixture["session"]["title"] = "different-run"
        code, result = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "session_binding_mismatch")

    def test_assistant_error_cannot_be_counted_as_completed(self):
        self.fixture["messages"][0]["info"]["error"] = {"name": "FixtureError"}
        code, receipt = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(receipt["status"], "unknown")
        self.assertNotIn("completed", receipt["evidence"])

    def test_idle_without_valid_assistant_payload_is_not_complete(self):
        self.fixture["messages"][0]["parts"] = [{"type": "text"}]
        code, receipt = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(receipt["status"], "unknown")
        self.assertNotIn("model_started", receipt["evidence"])
        self.assertNotIn("completed", receipt["evidence"])

    def test_old_terminal_message_does_not_complete_new_unfinished_turn(self):
        self.fixture["messages"].append({
            "info": {"role": "assistant", "agent": "reviewer",
                     "providerID": "openai", "modelID": "fake-model"},
            "parts": [{"type": "text", "text": "still working"}],
        })
        code, receipt = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(receipt["status"], "unknown")
        self.assertIn("model_started", receipt["evidence"])
        self.assertNotIn("completed", receipt["evidence"])

    def test_new_user_message_invalidates_old_terminal_completion(self):
        self.fixture["messages"].append({
            "info": {"role": "user"},
            "parts": [{"type": "text", "text": "new pending prompt"}],
        })
        code, receipt = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(receipt["status"], "unknown")
        self.assertNotIn("completed", receipt["evidence"])

    def test_busy_session_never_completes_even_with_old_terminal_message(self):
        self.fixture["statuses"][SID] = {"type": "busy"}
        code, receipt = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(receipt["status"], "running")
        self.assertNotIn("completed", receipt["evidence"])

    def test_pending_native_question_is_not_auto_answered(self):
        self.fixture["questions"] = [{"sessionID": SID, "id": "que_dummy"}]
        code, receipt = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(receipt["status"], "awaiting_human")
        self.assertTrue(all(method == "GET" for method, *_ in self.fixture["observed"]))

    def test_bad_auth_permissions_refuse_before_request(self):
        self.password.chmod(0o644)
        code, receipt = self.call()
        self.assertEqual(code, 64)
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(self.fixture["observed"], [])

    def test_redirect_does_not_leak_credentials(self):
        self.fixture["redirect"] = True
        code, receipt = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(receipt["status"], "unknown")
        self.assertEqual([path for _, path, _, _ in self.fixture["observed"]],
                         ["/global/health"])

    def test_oversized_response_fails_closed(self):
        self.fixture["oversize"] = True
        code, receipt = self.call()
        self.assertEqual(code, 75)
        self.assertEqual(receipt["status"], "unknown")
        self.assertNotIn("session_created", receipt["evidence"])


if __name__ == "__main__":
    unittest.main()
