import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "office").mkdir()
        (root / "approvals").mkdir()
        (root / "office" / "gate.json").write_text((REPO / "office" / "gate.json").read_text())
        self.env = {**os.environ, "AGENT_TEAM_ROOT": str(root)}

    def tearDown(self):
        self.tmp.cleanup()

    def gate(self, tool):
        return subprocess.run(
            [sys.executable, str(REPO / "scripts" / "gate.py")],
            input=json.dumps({"tool_name": tool}), text=True, capture_output=True, env=self.env,
        )

    def approve(self, kind):
        subprocess.run([sys.executable, str(REPO / "scripts" / "approve.py"), kind], env=self.env,
                       capture_output=True, check=True)

    def test_read_only_tool_is_allowed(self):
        self.assertEqual(self.gate("mcp__metricool__getAnalyticsDataByMetrics").returncode, 0)

    def test_publish_blocked_without_approvals(self):
        r = self.gate("mcp__metricool__createScheduledPost")
        self.assertEqual(r.returncode, 2)
        self.assertIn("qa", r.stderr)

    def test_publish_blocked_with_only_one_approval(self):
        self.approve("qa")
        r = self.gate("mcp__metricool__createScheduledPost")
        self.assertEqual(r.returncode, 2)
        self.assertIn("human", r.stderr)

    def test_publish_allowed_with_both_approvals(self):
        self.approve("qa")
        self.approve("human")
        self.assertEqual(self.gate("mcp__metricool__createScheduledPost").returncode, 0)

    def test_revoke_blocks_again(self):
        self.approve("qa")
        self.approve("human")
        subprocess.run([sys.executable, str(REPO / "scripts" / "approve.py"), "revoke"], env=self.env,
                       capture_output=True, check=True)
        self.assertEqual(self.gate("mcp__metricool__createScheduledPost").returncode, 2)


if __name__ == "__main__":
    unittest.main()
