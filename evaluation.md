# Implementation and Evaluation

## Files
| File | Purpose |
|---|---|
| `linebreak.py` | `baseline` (plain recursion), `optimized` (memoized recursion) |
| `test_linebreak.py` | 18 unit tests (`python -m unittest -v test_linebreak`) |
| `benchmark.py` | Timing experiments; writes `benchmark_results.csv` (`python benchmark.py`) |


## Implementation
The code follows the planning pseudocode directly. A line holding words `i..j` has width `sum(len) + (j - i)`. Its slack is `W - width`, and the last line costs 0. `baseline` tries every line that fits and recurses on the rest. `optimized` is identical plus a `memo` dictionary keyed by the starting word index, so each suffix is solved once.

Two additions beyond the pseudocode:
- **Infeasible input:** if a word is longer than `W`, no line can hold it, and all versions return `inf`.


## Testing
All 18 tests pass. They cover:
- **Hand-computed cases:** empty input, single word, everything on one line, exact-fit lines, forced breaks, a word exactly `W` long, and a case where greedy packing is not optimal.
- **Edge cases:** word longer than `W` (including mid-sequence), a free last line, non-negative penalties, inputs not mutated, and a 3000-word input that exercises deep recursion.
- **Randomized agreement:** 400 random inputs (up to 11 words, widths 4 to 25) compared against an independent brute-force oracle that enumerates every subset of break points. All three implementations match under both penalty functions.
- **Layout reconstruction:** 200 random inputs check that the rebuilt lines contain the same words in order, that every line fits, and that the recomputed cost equals the DP value.

## Benchmarking
Each time is the best of 3 runs, measured with `time.perf_counter`. Words are random lengths 2 to 8 with a fixed seed. The machine and Python version were not recorded, so absolute times will differ on yours; the trends are what matter.

### Experiment 1: baseline vs optimized (W = 40, about 8 words per line)
| n | Baseline (s) | Optimized (s) | Speedup |
|---:|---:|---:|---:|
| 5 | 0.000007 | 0.000005 | 1.5x |
| 10 | 0.000200 | 0.000011 | 17.6x |
| 15 | 0.006333 | 0.000017 | 365x |
| 20 | 0.196844 | 0.000024 | 8,233x |
| 25 | 6.111451 | 0.000052 | 117,982x |
| 30+ | skipped (cap of 5 s exceeded at n = 25) | 0.000038 at n = 30 | n/a |

Each +5 words multiplies baseline time by about 30x (0.0063 to 0.197 to 6.11), i.e. about 2x per added word. That is consistent with the predicted exponential growth. The memoized version is still under 0.1 ms at n = 60.

### Experiment 2: optimized only, fixed W = 80
| n | Memoized (s) | Bottom-up (s) |
|---:|---:|---:|
| 500 | 0.001892 | 0.001234 |
| 1,000 | 0.003821 | 0.002481 |
| 2,000 | 0.007829 | 0.005009 |
| 4,000 | 0.016069 | 0.010208 |
| 8,000 | 0.032546 | 0.020360 |

Doubling `n` doubles the time, so the growth is linear. With a fixed `W`, the inner loop stops after at most about `W/2` words, so the real cost is O(n * min(n, W)). The bottom-up version is about 1.6x faster because it avoids recursion overhead.

### Experiment 3: worst case, W = 10^9 (every word fits on one line)
| n | Memoized (s) | Time / n^2 (ns) |
|---:|---:|---:|
| 250 | 0.008975 | 143.6 |
| 500 | 0.038572 | 154.3 |
| 1,000 | 0.156545 | 156.5 |
| 2,000 | 0.628628 | 157.2 |
| 4,000 | 2.637051 | 164.8 |

Doubling `n` quadruples the time, and time / n^2 is roughly constant (about 155 ns). This confirms the Theta(n^2) worst case.

## Conclusions
- **Correctness:** the baseline and optimized agree with each other and with a brute-force oracle on all randomized tests.
- **Baseline is exponential:** it becomes unusable at about 25 words (6 s) and would take much longer for a real paragraph.
- **Memoization fixes this:** it removes repeated subproblems and gives a speedup of over 100,000x at n = 25.
- **Theta(n^2) is the worst case, not the typical one:** the planning bound is only reached when `W` is large enough for all words to share a line. 

