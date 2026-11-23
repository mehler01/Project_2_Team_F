"""Empirical running-time comparison. Run: python benchmark.py
Writes results to benchmark_results.csv and prints tables."""
import csv
import random
import sys
import time

from linebreak import baseline, optimized

TIME_CAP = 5.0       # stop growing baseline once one run exceeds this many seconds
REPEATS = 10          # take the best of several runs to reduce noise


def make_words(n, seed=1, lo=2, hi=8):
    rng = random.Random(seed)
    return ["x" * rng.randint(lo, hi) for _ in range(n)]


def timeit(f, words, width):
    best = float("inf")
    for _ in range(REPEATS):
        t = time.perf_counter()
        f(words, width)
        best = min(best, time.perf_counter() - t)
    return best


def main():
    sys.setrecursionlimit(20000)
    rows = []

    # Experiment 1: baseline vs optimized on small n (W = 40, ~8 words per line)
    print("Experiment 1: baseline vs optimized, W=40")
    print(f"{'n':>4} {'baseline (s)':>14} {'optimized (s)':>14} {'speedup':>10}")
    capped = False
    for n in range(5, 61, 5):
        w = make_words(n)
        o = timeit(optimized, w, 40)
        if not capped:
            b = timeit(baseline, w, 40)
            capped = b > TIME_CAP
            print(f"{n:>4} {b:>14.6f} {o:>14.6f} {b / o:>10.1f}x")
            rows.append(("exp1_W40", n, 40, b, o))
        else:
            print(f"{n:>4} {'(skipped)':>14} {o:>14.6f}")
            rows.append(("exp1_W40", n, 40, "", o))
        if capped and n >= 30:
            pass

    # Experiment 2: optimized alone, large n, fixed W=80 (expect ~linear in n)
    print("\nExperiment 2: optimized only, W=80 fixed")
    print(f"{'n':>6} {'memo (s)':>12} {'bottom-up (s)':>14}")
    for n in (500, 1000, 2000, 4000, 8000):
        w = make_words(n)
        m = timeit(optimized, w, 80)
        u = timeit(optimized_bottom_up, w, 80)
        print(f"{n:>6} {m:>12.6f} {u:>14.6f}")
        rows.append(("exp2_W80", n, 80, "", m))

    # Experiment 3: worst case for Theta(n^2): W huge so every word fits on one line
    print("\nExperiment 3: optimized only, W=10^9 (worst case, inner loop runs to n)")
    print(f"{'n':>6} {'memo (s)':>12} {'time / n^2 (ns)':>16}")
    for n in (250, 500, 1000, 2000, 4000):
        w = make_words(n)
        m = timeit(optimized, w, 10 ** 9)
        print(f"{n:>6} {m:>12.6f} {m / n ** 2 * 1e9:>16.2f}")
        rows.append(("exp3_Whuge", n, 10 ** 9, "", m))

    with open("benchmark_results.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["experiment", "n", "W", "baseline_s", "optimized_s"])
        wr.writerows(rows)


if __name__ == "__main__":
    main()
