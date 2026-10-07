# Shared rules (every agent reads this first)

## Method
1. **Data over hunches.** A decision cites a number, its time window and its baseline.
2. **One test per account at a time (the ladder).** Variant A and B run in the same period, alternating time slots; judged on the median, not on a single post; promoted at ≥ +20 % with ≥ 4 pieces per arm (`scripts/ladder.py`). Each account earns its own formula.
3. **A session is the minimum unit of content:** one set, one light, N poses.
4. **One action + one camera move per video prompt.**
5. **Every generation prompt carries a negative prompt** (base + character + niche).
6. **Cost per video is stated before generating.** Images are cheap; each video is a decision with a price.

## Certainty labels
**[V]** verified with our own data · **[S]** assumption / someone else's claim · **[?]** hypothesis.
A rule learned from a video or article starts as **[S]** and becomes **[V]** only after we measure it.

## Hard gates (enforced in code, not in prompts)
- Publishing tools are blocked by `scripts/gate.py` until today's queue has both approvals:
  `qa` (guardian) and `human` (the operator).
- Only the `publisher` agent has write access to the scheduler (`disallowedTools` on every other agent).

## Language
Prompts for image/video models in English. Everything else in the operator's language.
