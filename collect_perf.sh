#!/usr/bin/env bash
set -euo pipefail

OUTDIR="results"
mkdir -p $OUTDIR

OUTFILE="$OUTDIR/perf_sw_baseline_vs_opt.csv"
echo "type,run_id,N,threads,cycles,instructions,ipc,cache_refs,cache_misses,miss_rate,l1_misses,l1i_misses,llc_misses" > "$OUTFILE"

# Config
N=4096
THREADS=4
RUNS=10

EVENTS="cycles,instructions,cache-references,cache-misses,L1-dcache-load-misses,L1-icache-load-misses,LLC-load-misses"

extract_field() {
    local EVENT_NAME="$1"
    local BLOCK="$2"

    LINE=$(echo "$BLOCK" | grep "$EVENT_NAME" || true)

    # nothing found
    if [[ -z "$LINE" ]]; then
        echo 0
        return
    fi

    # perf -x, format: value,unit,event,run,metric
    FIELD=$(echo "$LINE" | awk -F',' '{print $1}')

    # unsupported?
    if [[ "$FIELD" == "<not supported>" || -z "$FIELD" ]]; then
        echo 0
    else
        echo "$FIELD"
    fi
}


run_perf() {
    local CMD="$1"
    local OUTPUT

    # Capture ALL perf output (perf prints to stderr!)
    OUTPUT=$(perf stat -x, -e $EVENTS $CMD 2>&1 1>/dev/null)

    # Extract fields safely
    CYCLES=$(extract_field "cycles" "$OUTPUT")
    INSTR=$(extract_field "instructions" "$OUTPUT")
    CREFS=$(extract_field "cache-references" "$OUTPUT")
    CMISS=$(extract_field "cache-misses" "$OUTPUT")
    L1D=$(extract_field "L1-dcache-load-misses" "$OUTPUT")
    L1I=$(extract_field "L1-icache-load-misses" "$OUTPUT")
    LLC=$(extract_field "LLC-load-misses" "$OUTPUT")

    # Compute IPC
    IPC=$(python3 - <<EOF
c=float("$CYCLES"); i=float("$INSTR")
print(i/c if c>0 else 0)
EOF
)

    # Compute miss rate
    MISS_RATE=$(python3 - <<EOF
cr=float("$CREFS"); cm=float("$CMISS")
print(cm/cr if cr>0 else 0)
EOF
)

    echo "$CYCLES,$INSTR,$IPC,$CREFS,$CMISS,$MISS_RATE,$L1D,$L1I,$LLC"
}

echo "Running PERF for baseline (Python baseline)..."
for r in $(seq 1 $RUNS); do
    CSV=$(run_perf "python3 baseline/sw_baseline.py $N")
    echo "baseline,$r,$N,$THREADS,$CSV" >> "$OUTFILE"
done

echo "Running PERF for optimized (Numba optimized)..."
for r in $(seq 1 $RUNS); do
    CSV=$(run_perf "python3 sw_opt.py $N")
    echo "optimized,$r,$N,$THREADS,$CSV" >> "$OUTFILE"
done

echo "Saved PERF CSV → $OUTFILE"
