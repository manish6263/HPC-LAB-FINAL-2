# #!/bin/bash

# # Exit immediately if a command exits with a non-zero status.
# set -e

# # Set the sequence length for the test
# # Start with a small-ish number (e.g., 1000) to test
# # You will need a larger number (e.g., 4000 or 8000) for the real report
# SEQ_LEN=20000

# echo "--- Building all executables ---"
# make clean
# make
# echo ""

# # --- 1. Run Baseline ---
# echo "--- Running Baseline (sw_baseline.c) ---"
# # We time this run to get the 'Baseline time' for the speedup calculation
# time ./baseline/sw_baseline $SEQ_LEN
# echo ""

# # --- 2. Run Optimized (1 Thread) ---
# echo "--- Running Optimized (1 Thread) ---"
# # Run optimized code with 1 thread to compare to baseline
# OMP_NUM_THREADS=1 time ./optimized/sw_opt $SEQ_LEN
# echo ""

# # --- 3. Run Scalability Test ---
# echo "--- Running Optimized (Scalability Test) ---"
# # Loop over different thread counts to get data for your scalability graph
# for threads in 1 2 4 8 16
# do
#     echo "Running with $threads threads..."
#     # Set the number of threads for OpenMP
#     OMP_NUM_THREADS=$threads time ./optimized/sw_opt $SEQ_LEN
#     echo ""
# done

# # --- 4. Profiling with Perf ---
# echo "--- Running 'perf' for detailed stats (16 Threads) ---"
# # This run will give you L1/L2/L3 miss rates and other stats
# # for your report 
# # 'perf stat -e' lists the events to monitor
# OMP_NUM_THREADS=16 perf stat -e L1-dcache-load-misses,L1-dcache-loads,cache-misses,cache-references,cycles,instructions ./optimized/sw_opt $SEQ_LEN
# echo ""

# echo "--- All runs complete ---"

#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- CONFIGURATION ---
# WARNING: Pure Python Baseline is SLOW. 
# N=2000 takes ~1-2 seconds in Python. 
# N=20000 would take ~20 minutes in Pure Python!
# Keep this small for testing, or comment out the baseline section for large runs.
SEQ_LEN=10000

echo "--- Setup ---"
make clean
echo ""

# --- 1. Run Baseline (Pure Python) ---
echo "--- Running Baseline (sw_baseline.py) ---"
# This uses the standard Python interpreter
time python3 baseline/sw_baseline.py $SEQ_LEN
echo ""

# --- 2. Run Optimized (1 Thread) ---
echo "--- Running Optimized (1 Thread) ---"
# We use NUMBA_NUM_THREADS to control Numba parallelism
NUMBA_NUM_THREADS=1 time python3 optimized/sw_opt.py $SEQ_LEN
echo ""

# --- 3. Run Scalability Test ---
echo "--- Running Optimized (Scalability Test) ---"
# Loop over different thread counts
for threads in 1 2 4 8 16
do
    echo "Running with $threads threads..."
    # Set Numba threads
    NUMBA_NUM_THREADS=$threads time python3 optimized/sw_opt.py $SEQ_LEN
    echo ""
done

# --- 4. Profiling with Perf ---
echo "--- Running 'perf' for detailed stats (16 Threads) ---"
# Note: Perf will include Python interpreter startup overhead.
# We increase N slightly here to make sure the kernel runs long enough to measure.
PERF_N=5000 
echo "Using N=$PERF_N for profiling to capture meaningful data..."

NUMBA_NUM_THREADS=16 perf stat -e cycles,instructions,cache-misses,L1-dcache-load-misses python3 optimized/sw_opt.py $PERF_N
echo ""

echo "--- All runs complete ---"