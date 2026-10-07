#!/usr/bin/env python3
"""PreToolUse hook: publishing tools only run when today's queue has every required approval.

Claude Code passes the pending tool call as JSON on stdin. Exit 0 = allow, exit 2 = block
(the message on stderr is shown to the agent). The rule lives in code, not in a prompt,
so an agent cannot talk its way past it.
"""
import datetime
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_TEAM_ROOT", Path(__file__).resolve().parent.parent))


def load_config():
    return json.loads((ROOT / "office" / "gate.json").read_text(encoding="utf-8"))


def todays_approvals():
    f = ROOT / "approvals" / f"{datetime.date.today().isoformat()}.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def main():
    try:
        call = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # not a tool call we understand; nothing to guard
    tool = call.get("tool_name", "")
    cfg = load_config()
    if not any(re.search(p, tool) for p in cfg["guarded_tool_patterns"]):
        return 0
    approvals = todays_approvals()
    missing = [a for a in cfg["required_approvals"] if not approvals.get(a)]
    if missing:
        sys.stderr.write(
            f"BLOCKED: '{tool}' needs today's approvals: {', '.join(missing)}. "
            "Run scripts/approve.py to record them, then retry.\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
