#!/usr/bin/env bash
set -euo pipefail

OUTDIR="results"
mkdir -p "$OUTDIR"

OUTFILE="$OUTDIR/results_sw_times.csv"
echo "N,threads,baseline_time,opt_time,speedup" > "$OUTFILE"

# ---- CONFIG ----
N_LIST=("1024" "2048" "4096")
THREADS_LIST=("1" "2" "4" "8" "12")
REPS=5

median() {
    printf "%s\n" "$@" | sort -n | awk '
        {a[NR]=$1}
        END {
            if (NR % 2 == 1) print a[(NR+1)/2];
            else print (a[NR/2] + a[(NR/2)+1]) / 2;
        }'
}

for N in "${N_LIST[@]}"; do
    for T in "${THREADS_LIST[@]}"; do

        echo "---- N=$N  T=$T ----"

        # ---------------- BASELINE ----------------
        base_times=()
        for r in $(seq 1 $REPS); do
            echo "Baseline run $r..."
            OUT=$(python3 baseline/sw_baseline.py "$N")
            TIME=$(echo "$OUT" | awk -F'Execution time: ' '/Execution time/ {print $2}' | awk '{print $1}')
            base_times+=("$TIME")
        done
        base_med=$(median "${base_times[@]}")

        # ---------------- OPTIMIZED ----------------
        export NUMBA_NUM_THREADS=$T
        opt_times=()
        for r in $(seq 1 $REPS); do
            echo "Optimized run $r..."
            OUT=$(python3 optimized/sw_opt.py "$N")
            TIME=$(echo "$OUT" | awk -F'Execution time: ' '/Execution time/ {print $2}' | awk '{print $1}')
            opt_times+=("$TIME")
        done
        opt_med=$(median "${opt_times[@]}")

        # ---------------- SPEEDUP ----------------
        speedup=$(python3 - << PY
b=$base_med
o=$opt_med
print(round(b/o,4))
PY
)

        echo "N=$N T=$T base=$base_med opt=$opt_med speedup=$speedup"
        echo "$N,$T,$base_med,$opt_med,$speedup" >> "$OUTFILE"

    done
done

echo "Saved timing results → $OUTFILE"