import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import ladder  # noqa: E402


def exp(a, b, **kw):
    posts = [{"arm": "A", "views": v} for v in a] + [{"arm": "B", "views": v} for v in b]
    return {"account": "acc", "variable": "hook", "control": "A", "test": "B", "posts": posts, **kw}


class LadderTest(unittest.TestCase):
    def test_winner_needs_20_percent_on_the_median(self):
        r = ladder.evaluate(exp([100, 100, 100, 100], [130, 125, 140, 120]))
        self.assertEqual(r["verdict"], "winner")
        self.assertEqual(r["winner"], "B")

    def test_one_viral_post_does_not_win(self):
        r = ladder.evaluate(exp([100, 100, 100, 100], [100, 105, 98, 100000]))
        self.assertEqual(r["verdict"], "no_effect")  # the median ignores the outlier

    def test_too_few_pieces_is_inconclusive(self):
        r = ladder.evaluate(exp([100, 100, 100], [200, 200, 200, 200]))
        self.assertEqual(r["verdict"], "inconclusive")

    def test_worse_test_arm_keeps_control(self):
        r = ladder.evaluate(exp([100, 100, 100, 100], [50, 60, 55, 52]))
        self.assertEqual(r["verdict"], "keep_control")

    def test_promote_writes_formula_and_history(self):
        with tempfile.TemporaryDirectory() as d:
            ladder.ROOT = Path(d)
            data, res = ladder.promote(exp([100] * 4, [150] * 4, values={"A": "statement", "B": "question"}))
            self.assertEqual(data["formula"]["hook"], "question")
            self.assertEqual(len(data["history"]), 1)
            self.assertTrue((Path(d) / "formulas" / "acc.json").exists())

    def test_inconclusive_is_not_promoted(self):
        with tempfile.TemporaryDirectory() as d:
            ladder.ROOT = Path(d)
            data, res = ladder.promote(exp([100] * 2, [150] * 2))
            self.assertIsNone(data)


if __name__ == "__main__":
    unittest.main()
