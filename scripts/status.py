#!/usr/bin/env python3
"""Status light for each agent. Usage: status.py <agent> <working|idle|waiting|blocked> ["task"]

Writes office/status.json so a dashboard (or a human running `status.py show`) can see
who is doing what, who is waiting on a decision and who is blocked.
"""
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_TEAM_ROOT", Path(__file__).resolve().parent.parent))
FILE = ROOT / "office" / "status.json"
STATES = {"working", "idle", "waiting", "blocked"}


def main(argv):
    data = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}
    if argv and argv[0] == "show":
        for name, s in sorted(data.items()):
            print(f"{name:12} {s['state']:8} {s['task']}")
        return 0
    if len(argv) < 2 or argv[1] not in STATES:
        print(__doc__)
        return 1
    data[argv[0]] = {
        "state": argv[1],
        "task": " ".join(argv[2:]),
        "updated": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
