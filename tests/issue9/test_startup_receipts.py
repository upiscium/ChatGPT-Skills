"""Behavioral receipt checks for Issue #9, with no real model or remote task."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "skills/opencode-bridge/scripts/run-headless-receipt.py"


class StartReceiptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="arca9-receipt-")
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.state = root / "state"
        self.state.mkdir(mode=0o700)
        self.cwd = root / "work"
        self.cwd.mkdir()
        self.binary = root / "opencode-fixture"
        self.binary.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys, time\n"
            "mode=sys.argv[-1]\n"
            "if mode == 'stall':\n"
            "    time.sleep(12)\n"
            "    sys.exit(0)\n"
            "if sys.stdin.read() != '':\n"
            "    sys.exit(99)\n"
            "if mode == 'no-session-event':\n"
            "    print(json.dumps({'type':'step_start','part':{'type':'step-start'}}), flush=True)\n"
            "    sys.exit(0)\n"
            "print(json.dumps({'type':'step_start','sessionID':'ses_fixtureA1',"
            "'part':{'type':'step-start'}}), flush=True)\n"
            "if mode == 'session-no-model':\n"
            "    sys.exit(0)\n"
            "if mode == 'model-stall':\n"
            "    time.sleep(12)\n"
            "    sys.exit(0)\n"
            "if mode == 'malformed':\n"
            "    print('NOT_JSON', flush=True)\n"
            "    sys.exit(0)\n"
            "if mode == 'failed':\n"
            "    sys.exit(17)\n"
            "print(json.dumps({'type':'text','sessionID':'ses_fixtureA1',"
            "'part':{'type':'text','text':'SECRET_FIXTURE_ONLY'}}), flush=True)\n"
            "if mode == 'model-then-malformed':\n"
            "    print('NOT_JSON', flush=True)\n"
            "    sys.exit(0)\n"
            "if mode == 'model-then-error':\n"
            "    print(json.dumps({'type':'error','sessionID':'ses_fixtureA1'}),flush=True)\n"
            "    sys.exit(0)\n"
            "sys.stderr.write(json.dumps(sys.argv[1:]))\n"
        )
        self.binary.chmod(0o755)
        self.runid = "test-run-9"

    def invoke(self, mode: str, *, startup: float = 1.0, runtime: float = 3.0,
               options: list[str] | None = None):
        argv = [sys.executable, str(RUNNER), "--run-id", self.runid,
                "--state-root", str(self.state), "--cwd", str(self.cwd),
                "--binary", str(self.binary), "--startup-seconds", str(startup),
                "--runtime-seconds", str(runtime), "--", *(options or []), mode]
        # Intentionally keep the parent pipe open: runner must not inherit it
        # into the OpenCode child.
        proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        try:
            code = proc.wait(timeout=6)
            return code, proc.stdout.read(), proc.stderr.read()
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.communicate(timeout=5)

    def events(self):
        state = self.state / self.runid
        data = (state / "receipt.jsonl").read_text()
        records = [json.loads(line) for line in data.splitlines()]
        self.assertTrue(all(e["schema"] == "arca-headless-receipt-v1" and
                            e["run_id"] == self.runid for e in records))
        return records

    def test_success_requires_real_session_and_model_evidence(self):
        code, _out, _err = self.invoke("complete",
                                       options=["--file", "packet with spaces.md"])
        self.assertEqual(code, 0)
        receipt = self.events()
        self.assertEqual([e["event"] for e in receipt],
                         ["launch_intent", "process_spawned", "opencode_initialized",
                          "session_created", "model_started", "completed"])
        self.assertEqual(receipt[-1]["session_id"], "ses_fixtureA1")
        self.assertGreater(receipt[1].get("start_ticks", 0), 0)
        self.assertIsInstance(receipt[1].get("boot_id"), str)
        self.assertNotIn("SECRET_FIXTURE_ONLY",
                         (self.state / self.runid / "receipt.jsonl").read_text())
        captured = [json.loads(x) for x in (self.state/self.runid/"stdout.jsonl").read_text().splitlines()]
        self.assertEqual(captured[1]["part"]["text"], "SECRET_FIXTURE_ONLY")
        self.assertEqual(json.loads((self.state/self.runid/"stderr.log").read_text()),
                         ["run", "--format", "json", "--file", "packet with spaces.md",
                          "complete"])
        for f in (self.state/self.runid).iterdir():
            self.assertEqual(stat.S_IMODE(f.stat().st_mode), 0o600, f)

    def test_exit_zero_without_model_cannot_be_reported_completed(self):
        code, _out, _err = self.invoke("session-no-model")
        self.assertEqual(code, 75)
        names = [e["event"] for e in self.events()]
        self.assertIn("session_created", names)
        self.assertNotIn("model_started", names)
        self.assertEqual(names[-1], "exited_without_verified_completion_unknown")

    def test_nonzero_model_exit_is_not_success(self):
        code, _out, _err = self.invoke("failed")
        self.assertEqual(code, 17)
        names = [e["event"] for e in self.events()]
        self.assertIn("session_created", names)
        self.assertNotIn("completed", names)
        self.assertEqual(names[-1], "exited_failure")

    def test_no_session_stall_retains_child_without_retry(self):
        code, _out, _err = self.invoke("stall", startup=0.2, runtime=1.0)
        self.assertEqual(code, 75)
        receipt = self.events()
        self.assertEqual([e["event"] for e in receipt][-1], "startup_stalled_unknown")
        self.assertTrue(receipt[-1]["child_retained"])
        pid = receipt[1]["pid"]
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            self.fail("ambiguous child was incorrectly terminated")
        finally:
            # The only cleanup here is the test's known disposable fixture PID.
            os.kill(pid, signal.SIGTERM)

    def test_model_stall_is_separate_from_startup(self):
        code, _out, _err = self.invoke("model-stall", startup=0.2, runtime=0.4)
        self.assertEqual(code, 75)
        receipt = self.events()
        names = [e["event"] for e in receipt]
        self.assertIn("session_created", names)
        self.assertEqual(names[-1], "runtime_stalled_unknown")
        self.assertNotIn("completed", names)
        os.kill(receipt[1]["pid"], signal.SIGTERM)

    def test_same_run_id_refuses_second_dispatch(self):
        self.assertEqual(self.invoke("complete")[0], 0)
        before = (self.state/self.runid/"receipt.jsonl").read_bytes()
        code, _out, err = self.invoke("complete")
        self.assertEqual(code, 73)
        self.assertIn("reconcile before retry", err)
        self.assertEqual((self.state/self.runid/"receipt.jsonl").read_bytes(), before)

    def test_unsafe_options_or_public_state_directory_are_rejected(self):
        for opt in ("--auto", "--format=json", "--model", "--variant=x", "--dir=/elsewhere"):
            with self.subTest(option=opt):
                code, _out, err = self.invoke("complete", options=[opt])
                self.assertEqual(code, 64)
                self.assertIn("unapproved OpenCode control", err)
                self.assertFalse((self.state/self.runid).exists())
        self.state.chmod(0o755)
        code, _out, err = self.invoke("complete")
        self.assertEqual(code, 64)
        self.assertIn("mode 0700", err)

    def test_exit_zero_without_session_is_not_completion_proof(self):
        code, _out, _err = self.invoke("no-session-event")
        self.assertEqual(code, 75)
        names = [event["event"] for event in self.events()]
        self.assertIn("opencode_initialized", names)
        self.assertNotIn("session_created", names)
        self.assertNotIn("completed", names)
        self.assertEqual(names[-1], "exited_without_verified_completion_unknown")

    def test_error_event_after_model_is_not_completion_proof(self):
        code, _out, _err = self.invoke("model-then-error")
        self.assertEqual(code, 75)
        names = [event["event"] for event in self.events()]
        self.assertIn("model_started", names)
        self.assertIn("model_error_observed", names)
        self.assertNotIn("completed", names)

    def test_invalid_output_after_model_is_not_completion_proof(self):
        code, _out, _err = self.invoke("model-then-malformed")
        self.assertEqual(code, 75)
        names = [event["event"] for event in self.events()]
        self.assertIn("model_started", names)
        self.assertNotIn("completed", names)
        self.assertEqual(names[-1], "exited_without_verified_completion_unknown")

    def test_invalid_output_is_not_session_or_completion_proof(self):
        code, _out, _err = self.invoke("malformed")
        self.assertEqual(code, 75)
        names = [e["event"] for e in self.events()]
        self.assertIn("session_created", names)
        self.assertNotIn("completed", names)


if __name__ == "__main__":
    unittest.main()
