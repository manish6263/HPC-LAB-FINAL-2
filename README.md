# Smith–Waterman Optimization — Final HPC Lab Project

## Authors
- **Adithya R Narayan (2024MCS2445)**
- **Manish Patel (2024MCS2460)**

This project implements an optimized Smith–Waterman (SW) local sequence alignment algorithm.
Starting from a slow Python baseline, we progressively optimized through:
- Numba JIT compilation
- Memory tiling (128×128 blocks)
- Wavefront (anti-diagonal) multicore parallelism
- Flattened DP matrix for cache efficiency
- Performance counter analysis using `perf`

---

## 📁 Directory Structure

```
.
├── baseline/
│   └── sw_baseline.py
├── optimized/
│   ├── sw_opt.py        # Optimized Numba + Parallel version
│   └── sw_opt.c         # Earlier C/OpenMP version (unused in final)
├── results/
│   ├── results_sw_times.csv
│   ├── perf_sw_baseline_vs_opt.csv
├── plots/
│   ├── speedup_vs_threads.png
│   ├── speedup_vs_N.png
│   ├── perf_ipc.png
│   └── perf_miss_rate.png
├── collect_times.sh
├── collect_perf.sh
├── plots.py
└── report.tex
```

---

## 🚀 1. Running the Baseline

Python baseline (slow, pure Python):

```
python3 baseline/sw_baseline.py N
```

Example:
```
python3 baseline/sw_baseline.py 2048
```

---

## ⚡ 2. Running the Optimized Version

Numba JIT + Tiling + Wavefront parallel:

```
python3 optimized/sw_opt.py N
```

Example:
```
python3 optimized/sw_opt.py 4096
```

Both programs generate:
- Final SW score
- Runtime in seconds

---

## 📊 3. Running Full Experiments (Timing + Speedup)

```
./collect_times.sh
```

This script:
- Tests multiple sequence lengths (1024, 2048, 4096)
- Tests multiple thread counts (1, 2, 4, 8, 12)
- Computes median runtimes for baseline & optimized
- Stores results in:

```
results/results_sw_times.csv
```

Plots can then be generated with:

```
python3 plots.py
```

---

## 🧪 4. Collecting Performance Counters (perf)

```
./collect_perf.sh
```

This collects:
- cycles
- instructions
- IPC
- cache-references
- cache-misses
- L1-dcache / L1-icache misses

Output is stored in:

```
results/perf_sw_baseline_vs_opt.csv
```

WSL2 does not support LLC counters — these appear as `0` or `<not supported>`.

---

## 📈 5. Plots Generated

### ✔️ Speedup vs Threads  
Shows parallel scaling across thread counts.

### ✔️ Speedup vs Sequence Length  
Shows how SW becomes more compute-bound as N grows.

### ✔️ IPC Comparison  
Higher IPC indicates more ILP.

### ✔️ Cache-Miss Rate Comparison  
Shows memory-boundedness of optimized implementation.

Generate all plots:

```
python3 plots.py
```

Outputs saved in `plots/`.

---

## 🏁 6. Summary of Optimization Achievements

| Feature | Baseline | Optimized |
|--------|----------|-----------|
| DP Matrix | Python list-of-lists | Flattened NumPy `int32` |
| Execution | Pure Python loops | Machine code (LLVM) |
| Cache locality | Poor | 128×128 tiling |
| Parallelism | None | Wavefront (anti-diagonal) |
| Speedup | 1× | **135×–170×** depending on N |

---

## 📚 7. Reproducibility

- Hardware: Intel Core i5-11400H (6C/12T)
- Software: Python 3.10, Numba, GCC, perf 5.15
- All scripts included:
  - `collect_times.sh`
  - `collect_perf.sh`
  - `plots.py`

---

## 📄 8. Report

Full analysis and technical explanation available in:

```
report.tex
```

---

## ✔️ End of README
