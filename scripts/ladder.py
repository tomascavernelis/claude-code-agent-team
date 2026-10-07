#!/usr/bin/env python3
"""The test ladder: find each account's own winning formula, one variable at a time.

  ladder.py evaluate experiments/<file>.json   # median vs. the account's own baseline
  ladder.py promote  experiments/<file>.json   # write the winner into formulas/<account>.json
  ladder.py show     <account>                 # the account's current formula + history

Rules (see docs/EXPERIMENT-LADDER.md):
  * one variable per account at a time, arms A (control) and B run in the same period
  * at least MIN_PIECES posts per arm
  * judged on the MEDIAN, never on a single post
  * an arm must beat the control median by at least MIN_LIFT to be promoted
"""
import datetime
import json
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_TEAM_ROOT", Path(__file__).resolve().parent.parent))
MIN_PIECES = 4
MIN_LIFT = 0.20


def evaluate(exp, min_pieces=MIN_PIECES, min_lift=MIN_LIFT):
    arms = {}
    for p in exp["posts"]:
        arms.setdefault(p["arm"], []).append(p["views"])
    control, test = exp["control"], exp["test"]
    out = {"account": exp["account"], "variable": exp["variable"],
           "medians": {a: statistics.median(v) for a, v in arms.items() if v},
           "pieces": {a: len(v) for a, v in arms.items()}}
    short = [a for a in (control, test) if len(arms.get(a, [])) < min_pieces]
    if short:
        need = {a: min_pieces - len(arms.get(a, [])) for a in short}
        return {**out, "verdict": "inconclusive", "reason": f"need more pieces: {need}"}
    base = out["medians"][control]
    if base <= 0:
        return {**out, "verdict": "inconclusive", "reason": "control median is 0"}
    lift = (out["medians"][test] - base) / base
    out["lift"] = round(lift, 3)
    if lift >= min_lift:
        return {**out, "verdict": "winner", "winner": test, "reason": f"+{lift:.0%} on the median"}
    if lift <= -min_lift:
        return {**out, "verdict": "keep_control", "winner": control, "reason": f"test arm {lift:.0%} on the median"}
    return {**out, "verdict": "no_effect", "winner": control,
            "reason": f"{lift:+.0%}: below the {min_lift:.0%} bar, keep control and test the next variable"}


def formula_path(account):
    return ROOT / "formulas" / f"{account}.json"


def load_formula(account):
    f = formula_path(account)
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"account": account, "formula": {}, "history": []}


def promote(exp):
    res = evaluate(exp)
    if res["verdict"] not in ("winner", "keep_control", "no_effect"):
        return None, res
    data = load_formula(exp["account"])
    value = exp["values"][res["winner"]] if "values" in exp else res["winner"]
    data["formula"][exp["variable"]] = value
    data["history"].append({"date": datetime.date.today().isoformat(), "variable": exp["variable"],
                            "winner": res["winner"], "medians": res["medians"], "lift": res.get("lift"),
                            "verdict": res["verdict"]})
    formula_path(exp["account"]).parent.mkdir(exist_ok=True)
    formula_path(exp["account"]).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data, res


def main(argv):
    if len(argv) < 2 or argv[0] not in ("evaluate", "promote", "show"):
        print(__doc__)
        return 1
    cmd, target = argv[0], argv[1]
    if cmd == "show":
        print(json.dumps(load_formula(target), indent=2, ensure_ascii=False))
        return 0
    exp = json.loads(Path(target).read_text(encoding="utf-8"))
    if cmd == "evaluate":
        print(json.dumps(evaluate(exp), indent=2))
        return 0
    data, res = promote(exp)
    print(json.dumps(res, indent=2))
    if data is None:
        print("Not promoted: the experiment is not conclusive yet.", file=sys.stderr)
        return 1
    print(json.dumps(data["formula"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
