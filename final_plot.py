import pandas as pd
import matplotlib.pyplot as plt
import os

plt.style.use("seaborn-v0_8")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 14

RESULTS = "results/results_sw_times.csv"
PERF = "results/perf_sw_baseline_vs_opt.csv"
OUT = "plots"
os.makedirs(OUT, exist_ok=True)

def save_plot(name):
    plt.savefig(os.path.join(OUT, name), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[Saved] {name}")

# ============================================================
# 1) SPEEDUP vs N
# ============================================================

def plot_speedup_vs_N():
    df = pd.read_csv(RESULTS)
    plt.figure()

    for T in sorted(df["threads"].unique()):
        d = df[df["threads"] == T]
        plt.plot(d["N"], d["speedup"], marker="o", label=f"T={T}")

    plt.xlabel("Sequence Length (N)")
    plt.ylabel("Speedup (Baseline / Optimized)")
    plt.title("Speedup vs Sequence Length")
    plt.grid(True)
    plt.legend()
    save_plot("speedup_vs_N.png")

# ============================================================
# 2) SPEEDUP vs THREADS
# ============================================================

def plot_speedup_vs_threads():
    df = pd.read_csv(RESULTS)

    plt.figure()
    for N in sorted(df["N"].unique()):
        d = df[df["N"] == N]
        plt.plot(d["threads"], d["speedup"], marker="o", label=f"N={N}")

    plt.xlabel("Threads")
    plt.ylabel("Speedup (Baseline / Optimized)")
    plt.title("Speedup vs Threads")
    plt.grid(True)
    plt.legend()
    save_plot("speedup_vs_threads.png")

# ============================================================
# 3) PERF — IPC COMPARISON
# ============================================================

def plot_ipc_comparison():
    perf = pd.read_csv(PERF)

    # Average 10 runs
    base = perf[perf["type"] == "baseline"].mean(numeric_only=True)
    opt = perf[perf["type"] == "optimized"].mean(numeric_only=True)

    labels = ["Baseline", "Optimized"]
    ipc_vals = [base["ipc"], opt["ipc"]]

    plt.figure()
    plt.bar(labels, ipc_vals, color=["gray", "blue"])
    plt.ylabel("IPC (Instructions per Cycle)")
    plt.title("IPC Comparison (Baseline vs Optimized)")
    for i, v in enumerate(ipc_vals):
        plt.text(i, v, f"{v:.3f}", ha='center', va='bottom', fontsize=12)
    save_plot("perf_ipc.png")

# ============================================================
# 4) PERF — CACHE MISS RATE COMPARISON
# ============================================================

def plot_cache_miss_rate():
    perf = pd.read_csv(PERF)

    base = perf[perf["type"] == "baseline"].mean(numeric_only=True)
    opt = perf[perf["type"] == "optimized"].mean(numeric_only=True)

    labels = ["Baseline", "Optimized"]
    miss_vals = [base["miss_rate"], opt["miss_rate"]]

    plt.figure()
    plt.bar(labels, miss_vals, color=["gray", "blue"])
    plt.ylabel("Cache Miss Rate (cache_misses / cache_refs)")
    plt.title("Cache Miss Rate Comparison")
    for i, v in enumerate(miss_vals):
        plt.text(i, v, f"{v:.3f}", ha='center', va='bottom', fontsize=12)
    save_plot("perf_miss_rate.png")

# ============================================================
# MAIN
# ============================================================

def main():
    print("Generating plots...")

    plot_speedup_vs_N()
    plot_speedup_vs_threads()
    plot_ipc_comparison()
    plot_cache_miss_rate()

    print("\nAll plots saved in ./plots/")

if __name__ == "__main__":
    main()
