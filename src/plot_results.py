"""Use pandas to plot benchmark_results.csv"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUT_DIR = Path("C:/Users/jnmeh/CMPSC_202/Project_2_Team_F/assets")
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(OUT_DIR / "benchmark_results.csv")
 
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
ax.set_xscale("log")
ax.set_yscale("log")
ax.plot(e3["n"], e3["optimized_s"], "s-", color="tab:green", label="Measured")
c = e3["optimized_s"].iloc[-1] / e3["n"].iloc[-1] ** 2
ax.plot(e3["n"], c * e3["n"] ** 2, "k--", alpha=0.6, label="c · n² reference")
ax.set_title("Optimized worst case, W = 10⁹")
ax.set_xlabel("Number of words (n)")
ax.set_ylabel("Time (s, log scale)")
ax.legend()
ax.grid(True, alpha=0.3)

fig.tight_layout()
plot_path = OUT_DIR / "benchmark_plot.png"
fig.savefig(plot_path, dpi=150)
print(f"Saved {plot_path}")
plt.show()