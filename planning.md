"""Use pandas to plot benchmark_results.csv"""
import pandas as pd
import matplotlib.pyplot as plt
 
df = pd.read_csv("benchmark_results.csv")   # columns: experiment, n, W, baseline_s, optimized_s
 
fig, axes = plt.subplots(1, 2, figsize=(16, 4.8))
 
# Experiment 1: baseline vs optimized (log y-axis shows exponential vs near-flat)
e1 = df[df["experiment"] == "exp1_W40"]
ax = axes[0]
ax.plot(e1["n"], e1["baseline_s"], "o-", label="Baseline (recursive)")
ax.plot(e1["n"], e1["optimized_s"], "s-", label="Optimized (memoized)")
ax.set_yscale("log")
ax.set_title("Baseline vs optimized (W = 40)")
ax.set_xlabel("Number of words (n)")
ax.set_ylabel("Time (s, log scale)")
ax.legend()
ax.grid(True, which="both", alpha=0.3)
 
# Experiment 2: worst case, W huge -> quadratic; dashed line is c * n^2 fit at the largest n
e3 = df[df["experiment"] == "exp3_Whuge"]
ax = axes[1]
ax.set_yscale("log")
ax.plot(e3["n"], e3["optimized_s"], "s-", color="tab:green", label="Measured")
c = e3["optimized_s"].iloc[-1] / e3["n"].iloc[-1] ** 2
ax.plot(e3["n"], c * e3["n"] ** 2, "k--", alpha=0.6, label="c · n² reference")
ax.set_title("Optimized worst case, W = 10⁹ (quadratic)")
ax.set_xlabel("Number of words (n)")
ax.set_ylabel("Time (s, log scale)")
ax.legend()
ax.grid(True, alpha=0.3)
 
fig.tight_layout()
fig.savefig("benchmark_plot.png", dpi=150)
print("Saved benchmark_plot.png")
plt.show()
