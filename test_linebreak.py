"""Test suite. Run: python -m unittest -v test_linebreak"""
import itertools
import random
import unittest

from linebreak import (INF, baseline, optimized, penalty)

IMPLS = [baseline, optimized, optimized_bottom_up]


def brute_force(words, width, penalty):
    """Independent oracle: enumerate every subset of break points."""
    n = len(words)
    if n == 0:
        return 0
    best = INF
    for mask in itertools.product([False, True], repeat=n - 1):
        total, start, ok = 0, 0, True
        breaks = [i + 1 for i, b in enumerate(mask) if b] + [n]
        for end in breaks:
            line = words[start:end]
            w = sum(map(len, line)) + len(line) - 1
            if w > width:
                ok = False
                break
            if end != n:
                total += penalty(width - w)
            start = end
        if ok:
            best = min(best, total)
    return best


class HandCheckedCases(unittest.TestCase):
    def check(self, words, width, linear, cubic):
        for f in IMPLS:
            with self.subTest(impl=f.__name__):
                self.assertEqual(f(words, width, linear_penalty), linear)
                self.assertEqual(f(words, width, cubic_penalty), cubic)

    def test_empty(self):
        self.check([], 10, 0, 0)

    def test_single_word(self):
        self.check(["hello"], 10, 0, 0)          # last line is free

    def test_everything_fits_one_line(self):
        self.check(["a", "b", "c"], 20, 0, 0)

    def test_exact_fit_lines(self):
        self.check(["aaa", "bbb", "ccc"], 7, 0, 0)   # "aaa bbb" / "ccc"

    def test_forced_breaks(self):
        # width 5: each 3-letter word alone, slack 2 on first two lines
        self.check(["aaa", "bbb", "ccc"], 5, 12, 16)

    def test_uneven_forced(self):
        # width 6: "aaaa" (slack 2) / "bb" (slack 4) / "cccc" last
        self.check(["aaaa", "bb", "cccc"], 6, 18, 72)

    def test_word_exactly_width(self):
        self.check(["abcde", "fg"], 5, 0, 0)     # "abcde" slack 0, "fg" last

    def test_greedy_is_not_optimal(self):
        # Greedy packs "aaa bb" then "c" then "ddddd"; DP can do better.
        words, W = ["aaa", "bb", "c", "ddddd"], 6
        expected = brute_force(words, W, cubic_penalty)
        for f in IMPLS:
            self.assertEqual(f(words, W, cubic_penalty), expected)


class EdgeCases(unittest.TestCase):
    def test_word_longer_than_width_is_infeasible(self):
        for f in IMPLS:
            with self.subTest(impl=f.__name__):
                self.assertEqual(f(["short", "extraordinarily"], 8), INF)

    def test_infeasible_word_in_middle(self):
        for f in IMPLS:
            self.assertEqual(f(["a", "toolongword", "b"], 5), INF)

    def test_width_zero_with_no_words(self):
        for f in IMPLS:
            self.assertEqual(f([], 0), 0)

    def test_last_line_never_penalized(self):
        for f in IMPLS:
            self.assertEqual(f(["x"], 1000), 0)

    def test_penalty_nonnegative(self):
        words = "the quick brown fox jumps over the lazy dog".split()
        for f in IMPLS:
            self.assertGreaterEqual(f(words, 12), 0)

    def test_input_not_mutated(self):
        words = ["a", "bb", "ccc"]
        copy = list(words)
        for f in IMPLS:
            f(words, 5)
        self.assertEqual(words, copy)

    def test_long_input_bottom_up_and_memo(self):
        words = ["word"] * 3000                     # deep recursion for memo version
        self.assertEqual(optimized(words, 40), optimized_bottom_up(words, 40))


class RandomizedAgreement(unittest.TestCase):
    def test_all_implementations_match_brute_force(self):
        rng = random.Random(303)
        for _ in range(400):
            n = rng.randint(0, 11)
            words = ["x" * rng.randint(1, 8) for _ in range(n)]
            width = rng.randint(4, 25)
            for pen in (linear_penalty, cubic_penalty):
                expected = brute_force(words, width, pen)
                for f in IMPLS:
                    self.assertEqual(f(words, width, pen), expected,
                                     (f.__name__, words, width))


class LayoutReconstruction(unittest.TestCase):
    def test_layout_is_valid_and_matches_cost(self):
        rng = random.Random(7)
        for _ in range(200):
            n = rng.randint(1, 30)
            words = ["y" * rng.randint(1, 9) for _ in range(n)]
            width = rng.randint(9, 30)
            for pen in (linear_penalty, cubic_penalty):
                cost, lines = optimized_with_layout(words, width, pen)
                self.assertEqual(cost, optimized_bottom_up(words, width, pen))
                self.assertEqual(" ".join(lines).split(), words)   # same words, same order
                self.assertTrue(all(len(l) <= width for l in lines))
                recomputed = sum(pen(width - len(l)) for l in lines[:-1])
                self.assertEqual(recomputed, cost)

    def test_layout_infeasible(self):
        self.assertEqual(optimized_with_layout(["abcdefgh"], 3), (INF, None))


if __name__ == "__main__":
    unittest.main()
