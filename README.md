# claude-code-agent-team

A template for running **a team of specialized AI agents with Claude Code** — each agent is a
Markdown file, they coordinate through shared files, and the one irreversible action
(publishing) is protected by a **hook that enforces human + QA approval in code**.

Extracted from a system I use to run **14+ social media accounts** (Facebook, Instagram, Threads,
TikTok, YouTube Shorts, X) as a single operator.

**Real output of the system it was extracted from** (Metricool data, 10 Facebook Pages, Sep 17 – Oct 6 2026):

| | |
|---|---|
| Short-form videos published | **448** (~22/day) |
| Reel views | **9.2 M** |
| Total content views | **15.7 M** |
| Followers gained | **30,000+** |

> This repository contains only the generic framework — no accounts, credentials or client data.

## What's inside

```
.claude/agents/      7 role definitions (researcher, analyst, producer, guardian, publisher, growth, finance)
.claude/settings.json  PreToolUse hook that guards the publishing tools
scripts/gate.py      the gate: blocks publish tools unless today has QA + human approvals
scripts/approve.py   records / inspects / revokes today's approvals
scripts/status.py    status light per agent (working / idle / waiting / blocked)
scripts/ladder.py    the test ladder: per-account A/B on medians, promotes winners into formulas/<account>.json
experiments/ formulas/  experiment definitions and each account's earned formula
office/              team config, shared rules, and one room (INBOX + BOARD) per agent
tests/               unit tests for the gate and the ladder (stdlib only)
docs/ARCHITECTURE.md the diagram and the reasoning behind each design decision
```

## Key ideas

1. **Roles as code.** `.claude/agents/*.md` — versioned, diffable, reviewable.
2. **Least privilege.** Every agent except `publisher` has the scheduler's write tools in `disallowedTools`.
3. **Safety in code, not prompts.** `scripts/gate.py` is a `PreToolUse` hook: no `qa` + `human` approval for today → exit code 2 → the tool call never happens.
4. **Async human-in-the-loop.** Each agent reads `INBOX.md` first and updates `BOARD.md` last. The human answers whenever.
5. **Visible state.** `scripts/status.py` is a one-line "traffic light" per agent.
6. **Epistemic hygiene.** Every claim is labelled `[V]` verified, `[S]` assumed, `[?]` hypothesis.
7. **A formula per account, found by never-ending testing.** See below.

## The test ladder — every account gets its own formula

Generic playbooks ("post at 7 pm with a question hook") are averages over accounts that don't
exist. Here every account is its own world, so the system **never stops testing**:

- **One variable at a time** per account (hook, format, length, caption, slot…).
- **A and B run in the same period**, alternating time slots, so the slot isn't the variable.
- **Judged on the median** against the account's own baseline — one viral outlier can't win.
- **≥ 4 pieces per arm and ≥ +20 % on the median** to promote. Otherwise keep the control and open the next rung.
- Winners accumulate in `formulas/<account>.json` with the full history of how each rule was earned.
- Rules that come from outside (a video, an article) start as `[S]` and become `[V]` only after we measure them.

```bash
python3 scripts/ladder.py evaluate experiments/example-hook-test.json
# {"verdict": "winner", "winner": "B", "lift": 0.483, "reason": "+48% on the median", ...}
python3 scripts/ladder.py promote experiments/example-hook-test.json   # -> formulas/account-a.json
```

Details and rationale: [docs/EXPERIMENT-LADDER.md](docs/EXPERIMENT-LADDER.md). The `analyst` agent owns the ladder.

## Quick start

Requirements: [Claude Code](https://claude.com/claude-code), Python 3.9+.

```bash
git clone <this repo> && cd claude-code-agent-team
python3 -m unittest discover -s tests -v      # 11 tests: approval gate + test ladder

claude                                        # open Claude Code in this folder
> use the analyst to report how yesterday's posts did
> use the guardian to review today's queue
```

Try the gate by hand:

```bash
echo '{"tool_name":"mcp__metricool__createScheduledPost"}' | python3 scripts/gate.py   # exit 2: blocked
python3 scripts/approve.py qa "12 posts checked, no duplicates"
python3 scripts/approve.py human
echo '{"tool_name":"mcp__metricool__createScheduledPost"}' | python3 scripts/gate.py   # exit 0: allowed
python3 scripts/status.py publisher working "scheduling today's queue"
python3 scripts/status.py show
```

## Adapting it to another job

Swap the roles. Support triage, lead-gen outreach, or content localisation use the same
shape: some read-only agents that analyse, one agent allowed to write, a QA agent that can
say no, and a hook that makes the dangerous step impossible without a human OK.
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#extending-it).

## License

MIT — see [LICENSE](LICENSE).
