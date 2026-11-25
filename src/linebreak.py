"""Line-breaking: split a sequence of words into lines of width W so the total
whitespace penalty is minimal. The last line costs nothing.

A line holding words with total length L and k words has width L + (k - 1)
(single spaces between words). Its slack is W - width, and its penalty is
penalty(slack). Every function returns the minimum total penalty, or
math.inf when some word is longer than W (no valid layout exists).

PENALTY NOTE: the planning document is inconsistent. The problem statement and
baseline use slack * 3, while the optimized pseudocode uses slack ** 3. Both
implementations here take a penalty function so they always agree. Change
DEFAULT_PENALTY to switch (tests cover both).
"""
import math
import sys

INF = math.inf


def linear_penalty(slack):
    """slack * 3, as in the problem statement and baseline pseudocode."""
    return slack * 3


def cubic_penalty(slack):
    """slack ** 3, as in the optimized pseudocode."""
    return slack ** 3


DEFAULT_PENALTY = linear_penalty


def baseline(words, width, penalty=None):
    """Plain recursion: try every line that fits, recurse on the rest.
    Time O(2^n) worst case (subproblems recomputed), O(n) stack space."""
    penalty = penalty or DEFAULT_PENALTY
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


def optimized(words, width, penalty=None):
    """Top-down DP: same recursion as baseline plus a memo table keyed by the
    starting word index. Each index is solved once: O(n * k) time where k is the
    max words per line (k <= n, so O(n^2) worst case), O(n) space."""
    penalty = penalty or DEFAULT_PENALTY
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


def optimized_bottom_up(words, width, penalty=None):
    """Iterative DP (no recursion): dp[i] = best penalty for words[i:].
    Used as an extra cross-check and for very large inputs."""
    penalty = penalty or DEFAULT_PENALTY
    n = len(words)
    dp = [INF] * (n + 1)
    dp[n] = 0
    for i in range(n - 1, -1, -1):
        c = 0
        for j in range(i, n):
            c += len(words[j]) + 1
            if c - 1 > width:
                break
            cost = 0 if j == n - 1 else penalty(width - (c - 1))
            dp[i] = min(dp[i], cost + dp[j + 1])
    return dp[0]


def optimized_with_layout(words, width, penalty=None):
    """Bottom-up DP that also reconstructs the lines.
    Returns (min_penalty, list_of_lines) or (inf, None) if infeasible."""
    penalty = penalty or DEFAULT_PENALTY
    n = len(words)
    dp = [INF] * (n + 1)
    nxt = [n] * (n + 1)
    dp[n] = 0
    for i in range(n - 1, -1, -1):
        c = 0
        for j in range(i, n):
            c += len(words[j]) + 1
            if c - 1 > width:
                break
            cost = 0 if j == n - 1 else penalty(width - (c - 1))
            if cost + dp[j + 1] < dp[i]:
                dp[i] = cost + dp[j + 1]
                nxt[i] = j + 1
    if dp[0] == INF:
        return INF, None
    lines, i = [], 0
    while i < n:
        lines.append(" ".join(words[i:nxt[i]]))
        i = nxt[i]
    return dp[0], lines
