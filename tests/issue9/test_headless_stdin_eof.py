"""Issue #9: prevent non-TTY stdin EOF hangs in Arca's headless CLI launcher."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "skills" / "opencode-bridge" / "scripts" / "run-headless.sh"


class HeadlessStdinEOFTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="arca-headless-eof-")
        self.addCleanup(self.temp.cleanup)
        self.fake = Path(self.temp.name) / "opencode"
        self.fake.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "eof = sys.stdin.read()\n"
            "print(json.dumps({'args': sys.argv[1:], 'stdin': eof}))\n"
            "sys.exit(int(os.environ.get('FAKE_OPEN_CODE_EXIT', '0')))\n"
        )
        self.fake.chmod(0o755)

    def start(self, command: list[str], env: dict[str, str] | None = None):
        # Keep the writer of stdin OPEN until the child exits. On the old
        # Arca path (without </dev/null) this is the cause of the stall.
        return subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=env,
        )

    def test_unprotected_fake_cli_blocks_waiting_for_eof(self):
        process = self.start([str(self.fake), "run", "probe"])
        try:
            with self.assertRaises(subprocess.TimeoutExpired):
                process.wait(timeout=0.4)
        finally:
            process.kill()
            process.communicate(timeout=3)

    def test_wrapper_closes_open_socket_stdin_and_forwards_argv(self):
        args = ["--dir", "/isolated/work tree", "--file", "packet with spaces.md",
                "literal ; and | without shell interpolation"]
        process = self.start(["sh", str(WRAPPER), str(self.fake), *args])
        try:
            code = process.wait(timeout=3)
            self.assertEqual(code, 0, process.stderr.read())
            payload = json.loads(process.stdout.read())
            self.assertEqual(payload["args"], ["run", *args])
            self.assertEqual(payload["stdin"], "")
            self.assertNotIn("--auto", payload["args"])
            self.assertNotIn("--model", payload["args"])
            self.assertNotIn("--variant", payload["args"])
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=3)

    def test_wrapper_preserves_child_exit_code(self):
        env = dict(os.environ, FAKE_OPEN_CODE_EXIT="17")
        process = self.start(["sh", str(WRAPPER), str(self.fake), "probe"], env=env)
        try:
            self.assertEqual(process.wait(timeout=3), 17)
            payload = json.loads(process.stdout.read())
            self.assertEqual(payload["stdin"], "")
            self.assertEqual(payload["args"], ["run", "probe"])
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=3)

    def test_wrapper_rejects_unverified_binary_identity(self):
        for binary, expected_exit in (("opencode", 64), ("/nonexistent/opencode", 69)):
            with self.subTest(binary=binary):
                process = self.start(["sh", str(WRAPPER), binary, "prompt"])
                try:
                    self.assertEqual(process.wait(timeout=3), expected_exit)
                    self.assertIn("OpenCode executable", process.stderr.read())
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.communicate(timeout=3)

    def test_bridge_and_review_guidance_pin_the_same_rule(self):
        transport = (ROOT / "skills/opencode-bridge/references/transport.md").read_text()
        bridge = (ROOT / "skills/opencode-bridge/SKILL.md").read_text()
        reviewer = (ROOT / "skills/opencode-reviewer/references/launch.md").read_text()
        for item in (transport, bridge, reviewer):
            self.assertIn("stdin=subprocess.DEVNULL", item)
            self.assertIn("</dev/null", item)
        self.assertIn("startup_stalled/unknown", transport)
        self.assertIn("session_created", transport)
        self.assertIn("Do not kill by name", transport)
        self.assertIn("scripts/run-headless.sh", transport)
        self.assertIn("scripts/run-headless-receipt.py", transport)
        self.assertIn("scripts/run-headless-receipt.py", bridge)


if __name__ == "__main__":
    unittest.main()
