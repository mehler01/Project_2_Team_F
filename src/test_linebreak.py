"""Test suite. Run: python -m unittest -v test_linebreak

The penalty for a non-last line is 3 * slack (slack = width - line width);
the last line is free.
"""
import itertools
import random
import sys
import unittest

from linebreak import INF, baseline, optimized

IMPLS = [baseline, optimized]


def brute_force(words, width):
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
                total += 3 * (width - w)
            start = end
        if ok:
            best = min(best, total)
    return best


class HandCheckedCases(unittest.TestCase):
    def check(self, words, width, expected):
        for f in IMPLS:
            with self.subTest(impl=f.__name__):
                self.assertEqual(f(words, width), expected)

    def test_empty(self):
        self.check([], 10, 0)

    def test_single_word(self):
        self.check(["hello"], 10, 0)              # last line is free

    def test_everything_fits_one_line(self):
        self.check(["a", "b", "c"], 20, 0)

    def test_exact_fit_lines(self):
        self.check(["aaa", "bbb", "ccc"], 7, 0)   # "aaa bbb" / "ccc"

    def test_forced_breaks(self):
        # width 5: each 3-letter word alone, slack 2 on first two lines
        self.check(["aaa", "bbb", "ccc"], 5, 12)  # 3*2 + 3*2

    def test_uneven_forced(self):
        # width 6: "aaaa" (slack 2) / "bb" (slack 4) / "cccc" last
        self.check(["aaaa", "bb", "cccc"], 6, 18)  # 3*2 + 3*4

    def test_word_exactly_width(self):
        self.check(["abcde", "fg"], 5, 0)         # "abcde" slack 0, "fg" last

    def test_penalty_is_three_times_slack(self):
        # width 2: "a" (slack 1) / "b" last
        self.check(["a", "b"], 2, 3)

    def test_choice_between_layouts(self):
        # width 6: "aaa bb" (slack 0) / "c" (slack 5) / "ddddd" last = 15
        #     vs  "aaa" (slack 3) / "bb c" (slack 2) / "ddddd" last = 15
        words, W = ["aaa", "bb", "c", "ddddd"], 6
        self.check(words, W, 15)
        self.assertEqual(brute_force(words, W), 15)


class EdgeCases(unittest.TestCase):
    def test_word_longer_than_width_is_infeasible(self):
        for f in IMPLS:
            with self.subTest(impl=f.__name__):
                self.assertEqual(f(["short", "extraordinarily"], 8), INF)

    def test_infeasible_word_in_middle(self):
        for f in IMPLS:
            with self.subTest(impl=f.__name__):
                self.assertEqual(f(["a", "toolongword", "b"], 5), INF)

    def test_infeasible_single_word(self):
        for f in IMPLS:
            with self.subTest(impl=f.__name__):
                self.assertEqual(f(["abcdefgh"], 3), INF)

    def test_width_zero_with_no_words(self):
        for f in IMPLS:
            with self.subTest(impl=f.__name__):
                self.assertEqual(f([], 0), 0)

    def test_last_line_never_penalized(self):
        for f in IMPLS:
            with self.subTest(impl=f.__name__):
                self.assertEqual(f(["x"], 1000), 0)

    def test_penalty_nonnegative(self):
        words = "the quick brown fox jumps over the lazy dog".split()
        for f in IMPLS:
            with self.subTest(impl=f.__name__):
                self.assertGreaterEqual(f(words, 12), 0)

    def test_input_not_mutated(self):
        words = ["a", "bb", "ccc"]
        copy = list(words)
        for f in IMPLS:
            f(words, 5)
        self.assertEqual(words, copy)


class OptimizedSpecific(unittest.TestCase):
    def test_long_input_deep_recursion(self):
        # 3000 words forces recursion depth ~3000; baseline would be exponential,
        # so only the memoized version is run. Each line holds 8 words
        # (8*4 + 7 = 39 chars), slack 1 -> 374 penalized lines * 3 = 1122.
        words = ["word"] * 3000
        self.assertEqual(optimized(words, 40), 374 * 3)

    def test_recursion_limit_restored(self):
        before = sys.getrecursionlimit()
        optimized(["word"] * 3000, 40)
        self.assertEqual(sys.getrecursionlimit(), before)

    def test_recursion_limit_restored_on_infeasible(self):
        before = sys.getrecursionlimit()
        optimized(["a", "toolongword"], 5)
        self.assertEqual(sys.getrecursionlimit(), before)


class RandomizedAgreement(unittest.TestCase):
    def test_all_implementations_match_brute_force(self):
        rng = random.Random(303)
        for _ in range(400):
            n = rng.randint(0, 11)
            words = ["x" * rng.randint(1, 8) for _ in range(n)]
            width = rng.randint(4, 25)
            expected = brute_force(words, width)
            for f in IMPLS:
                self.assertEqual(f(words, width), expected,
                                 (f.__name__, words, width))

    def test_baseline_matches_optimized_on_medium_inputs(self):
        rng = random.Random(7)
        for _ in range(100):
            n = rng.randint(12, 16)
            words = ["y" * rng.randint(1, 9) for _ in range(n)]
            width = rng.randint(9, 30)
            self.assertEqual(baseline(words, width), optimized(words, width),
                             (words, width))


if __name__ == "__main__":
    unittest.main()