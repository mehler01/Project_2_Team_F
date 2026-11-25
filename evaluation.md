# Implementation and Evaluation

## Files
| File | Purpose |
|---|---|
| `linebreak.py` | `baseline` (plain recursion), `optimized` (memoized recursion) |
| `test_linebreak.py` | 21 unit tests (`python -m unittest -v test_linebreak`) |
| `benchmark.py` | Timing experiments; writes `benchmark_results.csv` to `assets/` (`python benchmark.py`) |
| `plot_results.py` | Reads the CSV and writes `benchmark_plot.png` to `assets/` |


## Implementation
The code follows the planning pseudocode directly. A line holding words `i..j` has width `sum(len) + (j - i)`. Its slack is `W - width`, its penalty is `3 * slack`, and the last line costs 0. `baseline` tries every line that fits and recurses on the rest. `optimized` is identical plus a `memo` dictionary keyed by the starting word index, so each suffix is solved once.

Two additions beyond the pseudocode:
- **Infeasible input:** if a word is longer than `W`, no line can hold it, and both versions return `inf`.
- **Recursion limit:** `optimized` recurses up to `n` levels deep, so it temporarily raises Python's recursion limit to at least `n + 1000` and restores it afterwards, even when the input is infeasible.

## Testing
All 21 tests pass. They cover:
- **Hand-computed cases (9):** empty input, single word, everything on one line, exact-fit lines, forced breaks, uneven forced breaks, a word exactly `W` long, the penalty being 3 × slack, and a case with two equally good layouts (cost 15) that is also checked against the brute-force oracle.
- **Edge cases (7):** a word longer than `W` (alone, at the end, and mid-sequence), empty input with `W = 0`, a free last line, non-negative penalties, and inputs not being mutated.
- **Optimized-specific (3):** a 3000-word input that exercises deep recursion, with a hand-computed answer of 1122 (374 penalized lines × 3), plus checks that the recursion limit is restored after both a normal and an infeasible call.
- **Randomized agreement (2):** 400 random inputs (up to 11 words, widths 4 to 25) compared against an independent brute-force oracle that enumerates every subset of break points, and 100 random medium inputs (12 to 16 words) where `baseline` and `optimized` are compared directly. All match.

## Benchmarking
Each time is the best of 10 runs, measured with `time.perf_counter`. Words are random lengths 2 to 8 with a fixed seed. The machine and Python version were not recorded, so absolute times will differ on yours; the trends are what matter.

### Experiment 1: baseline vs optimized (W = 40, about 8 words per line)
| n | Baseline (s) | Optimized (s) | Speedup |
|---:|---:|---:|---:|
| 5 | 0.0000056 | 0.0000054 | 1.0x |
| 10 | 0.000171 | 0.0000085 | 20x |
| 15 | 0.005616 | 0.0000150 | 374x |
| 20 | 0.170448 | 0.0000211 | 8,078x |
| 25 | 5.386800 | 0.0000427 | ~126,000x |
| 30 | skipped (5 s cap exceeded at n = 25) | 0.0000347 | n/a |
| 35 | skipped | 0.0000555 | n/a |
| 40 | skipped | 0.0000462 | n/a |
| 45 | skipped | 0.0000533 | n/a |
| 50 | skipped | 0.0000592 | n/a |

Each +5 words multiplies baseline time by about 31x (0.000171 to 0.0056 to 0.170 to 5.39, ratios of 33x, 30x, and 32x), i.e. about 2x per added word. That is consistent with the predicted exponential growth. The memoized version stays under 0.06 ms all the way to n = 50.

### Experiment 2: worst case, W = 10^9 (every word fits on one line)
| n | Memoized (s) | Time / n^2 (ns) |
|---:|---:|---:|
| 250 | 0.007540 | 120.6 |
| 500 | 0.033306 | 133.2 |
| 1,000 | 0.137328 | 137.3 |
| 2,000 | 0.561917 | 140.5 |
| 4,000 | 2.278476 | 142.4 |
| 8,000 | 9.175963 | 143.4 |
| 16,000 | 36.732621 | 143.5 |

Doubling `n` roughly quadruples the time (the ratio falls from 4.4x at the smallest sizes to 4.00x at the largest), and time / n^2 levels off at about 143 ns. This confirms the Theta(n^2) worst case. The slightly lower values at small `n` are fixed overhead that is amortized away as `n` grows.

## Conclusions
- **Correctness:** `baseline` and `optimized` agree with each other and with a brute-force oracle on all randomized tests.
- **Baseline is exponential:** it becomes unusable at about 25 words (5.4 s) and would take far longer for a real paragraph.
- **Memoization fixes this:** it removes repeated subproblems and gives a speedup of roughly 126,000x at n = 25.
- **Theta(n^2) is the worst case, not the typical one:** the planning bound is only reached when `W` is large enough for all words to share a line. For realistic widths the cost is O(n * W) and effectively linear in `n`.
- **Limitations:** timings are from one machine in pure Python, and the baseline was capped at 5 s per run. A single `W = 40` workload with random word lengths 2 to 8 is one workload, not all.