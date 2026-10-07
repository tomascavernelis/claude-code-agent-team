#!/usr/bin/env python3
"""Record or inspect today's approvals.

  approve.py qa "checked 12 posts, no duplicates"
  approve.py human
  approve.py status
  approve.py revoke
"""
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_TEAM_ROOT", Path(__file__).resolve().parent.parent))
FILE = ROOT / "approvals" / f"{datetime.date.today().isoformat()}.json"


def read():
    return json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd, note = argv[0], " ".join(argv[1:])
    data = read()
    if cmd in ("qa", "human"):
        data[cmd] = {"at": datetime.datetime.now().isoformat(timespec="seconds"), "note": note}
        FILE.parent.mkdir(exist_ok=True)
        FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    elif cmd == "revoke":
        FILE.unlink(missing_ok=True)
        data = {}
    elif cmd != "status":
        print(__doc__)
        return 1
    print(json.dumps({"date": FILE.stem, "approvals": data}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
