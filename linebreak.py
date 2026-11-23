"""Line-breaking: split a sequence of words into lines of width W so the total
whitespace penalty is minimal. The last line costs nothing.

A line holding words with total length L and k words has width L + (k - 1)
(single spaces between words). Its slack is W - width, and its penalty is
penalty(slack). Every function returns the minimum total penalty, or
math.inf when some word is longer than W (no valid layout exists).
"""
import math
import sys

INF = math.inf


def penalty(slack):
    """slack * 3, as in the problem statement and baseline pseudocode."""
    return slack * 3

def baseline(words, width):
    """Plain recursion: try every line that fits, recurse on the rest.
    Time O(2^n) worst case (subproblems recomputed), O(n) stack space."""
    n = len(words)

    def recursive(i):
        if i == n:                      # no words left -> no penalty
            return 0
        best = INF
        c = 0                           # chars used, counting a trailing space per word
        for j in range(i, n):
            c += len(words[j]) + 1
            if c - 1 > width:           # real width is c - 1 (no trailing space)
                break
            cost = 0 if j == n - 1 else penalty(width - (c - 1))
            best = min(best, cost + recursive(j + 1))
        return best

    return recursive(0)


def optimized(words, width):
    """Top-down DP: same recursion as baseline plus a memo table keyed by the
    starting word index. Each index is solved once: O(n * k) time where k is the
    max words per line (k <= n, so O(n^2) worst case), O(n) space."""
    n = len(words)
    memo = {}
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, n + 1000))   # recursion depth can reach n

    def recursive(i):
        if i == n:
            return 0
        if i in memo:
            return memo[i]
        best = INF
        c = 0
        for j in range(i, n):
            c += len(words[j]) + 1
            if c - 1 > width:
                break
            cost = 0 if j == n - 1 else penalty(width - (c - 1))
            best = min(best, cost + recursive(j + 1))
        memo[i] = best
        return best

    try:
        return recursive(0)
    finally:
        sys.setrecursionlimit(old_limit)
