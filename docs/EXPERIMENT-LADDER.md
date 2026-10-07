# The test ladder: every account gets its own formula

Most social media playbooks say "post at 7 pm with a question hook". That is an average over
accounts that do not exist. In a multi-account operation **every account is its own world** —
different audience, different format that works, different slot. So instead of copying one
playbook to all of them, the system *never stops testing* and builds a formula per account.

## The loop

```
for each account:
    pick ONE variable (hook, format, length, caption style, posting slot, ...)
    run arm A (control = current formula) and arm B (change) in the SAME period,
        alternating time slots so the slot itself is not the variable
    wait until each arm has >= 4 pieces and the platform's data has settled
    compare MEDIANS (never a single post) against the account's own baseline
    if B beats A by >= +20 %  -> B enters the formula        (ladder.py promote)
    if not                    -> keep A, move to the next variable
    open the next rung; repeat forever
```

Result: `formulas/<account>.json` — a living record of what works **for that account**, with the
full history (date, variable, medians, lift) of how each rule was earned.

## Why these rules

| Rule | What it prevents |
|---|---|
| One variable at a time per account | Not knowing which change caused the result |
| A and B in the same period, slots alternating | Confusing a good week or a good time slot with a good idea |
| Median, not mean or best post | One viral outlier "proving" a bad idea |
| ≥ 4 pieces per arm | Deciding on noise |
| +20 % bar on the median | Promoting differences that are inside the normal variation |
| Never compare account X's A with account Y's B | Cross-account contamination — each account is its own world |
| Rules learned from outside start as `[S]`, become `[V]` only after we measure them | Folklore hardening into "facts" |

## Use it

```bash
python3 scripts/ladder.py evaluate experiments/example-hook-test.json
python3 scripts/ladder.py promote  experiments/example-hook-test.json   # writes formulas/account-a.json
python3 scripts/ladder.py show     account-a
```

The `analyst` agent owns the ladder: it closes rungs, records the winner and proposes the next
variable for each account. The numbers in `experiments/example-hook-test.json` are synthetic.
