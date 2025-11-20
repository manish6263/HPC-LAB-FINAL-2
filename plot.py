import matplotlib.pyplot as plt
import numpy as np

# --- Data from your N=10,000 run ---
baseline_time = 55.076139
threads = [1, 2, 4, 8, 16]
opt_times = [0.555690, 0.294294, 0.182777, 0.157056, 0.262780]

# Calculate Speedups
# 1. Total Speedup (Baseline / Opt Time)
total_speedups = [baseline_time / t for t in opt_times]

# 2. Parallel Scalability (Opt 1-Thread / Opt N-Threads)
# This measures how well the code uses extra cores, ignoring the algorithmic speedup
scaling_speedups = [opt_times[0] / t for t in opt_times]

# --- Plot 1: Parallel Scalability (Strong Scaling) ---
plt.figure(figsize=(10, 6))
plt.plot(threads, scaling_speedups, marker='o', linewidth=2, markersize=8, label='Measured Speedup')
# Ideal scaling line (linear)
plt.plot(threads, threads, linestyle='--', color='gray', alpha=0.7, label='Ideal Linear Scaling')

plt.title(f'Strong Scaling Analysis (N=10,000)\nSpeedup relative to Optimized 1-Thread', fontsize=14)
plt.xlabel('Number of Threads', fontsize=12)
plt.ylabel('Speedup Factor (vs 1-Thread)', fontsize=12)
plt.xticks(threads)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Annotate the peak
peak_idx = np.argmax(scaling_speedups)
peak_val = scaling_speedups[peak_idx]
plt.annotate(f'Peak: {peak_val:.2f}x\n(8 Threads)', 
             xy=(threads[peak_idx], peak_val), 
             xytext=(threads[peak_idx], peak_val+0.5),
             arrowprops=dict(facecolor='black', shrink=0.05),
             horizontalalignment='center')

plt.savefig('scalability_plot.png', dpi=300)
print("Generated scalability_plot.png")

# --- Plot 2: Execution Time Comparison (Log Scale) ---
plt.figure(figsize=(10, 6))

labels = ['Baseline'] + [f'Opt ({t}T)' for t in threads]
times = [baseline_time] + opt_times
colors = ['red'] + ['blue']*len(threads)

bars = plt.bar(labels, times, color=colors, alpha=0.8)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., 1.05*height,
             f'{height:.2f}s',
             ha='center', va='bottom', rotation=0)

plt.yscale('log')  # Log scale is crucial because 55s vs 0.15s is huge
plt.title('Execution Time Comparison (Log Scale)', fontsize=14)
plt.ylabel('Time (seconds) - Log Scale', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.5)

# Add speedup annotation for the best run
best_time = min(opt_times)
total_speedup = baseline_time / best_time
plt.text(0.5, 0.8, f"Max Speedup vs Baseline:\n{total_speedup:.1f}x", 
         transform=plt.gca().transAxes, fontsize=14, 
         bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="black", alpha=0.8))

plt.savefig('execution_time_plot.png', dpi=300)
print("Generated execution_time_plot.png")
