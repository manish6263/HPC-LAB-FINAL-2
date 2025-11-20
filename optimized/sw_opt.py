import sys
import time
import numpy as np
from numba import njit, prange

# --- Configuration ---
MATCH = 2
MISMATCH = -1
GAP = -2
TILE_SIZE = 128

@njit(fastmath=True)
def process_tile(start_i, start_j, end_i, end_j, width, H, seq1, seq2):
    """
    Compute a single tile (block) of the matrix sequentially.
    Returns the maximum score found in this tile.
    """
    local_max = 0
    
    for i in range(start_i, end_i):
        curr_row_idx = i * width
        prev_row_idx = (i - 1) * width
        
        char1 = seq1[i - 1]
        
        for j in range(start_j, end_j):
            char2 = seq2[j - 1]
            
            # Calculate Score
            s = MATCH if char1 == char2 else MISMATCH
            
            diag = H[prev_row_idx + j - 1] + s
            up = H[prev_row_idx + j] + GAP
            left = H[curr_row_idx + j - 1] + GAP
            
            score = 0
            if diag > score: score = diag
            if up > score: score = up
            if left > score: score = left
            
            H[curr_row_idx + j] = score
            
            if score > local_max:
                local_max = score
                
    return local_max

@njit(parallel=True, fastmath=True)
def smith_waterman_optimized(seq1_arr, seq2_arr, N):
    rows = N + 1
    cols = N + 1
    H = np.zeros(rows * cols, dtype=np.int32)
    
    n_tiles_i = (N + TILE_SIZE - 1) // TILE_SIZE
    n_tiles_j = (N + TILE_SIZE - 1) // TILE_SIZE
    
    global_max = 0
    total_wavefronts = n_tiles_i + n_tiles_j - 1
    
    for k in range(total_wavefronts):
        start_ti = max(0, k - n_tiles_j + 1)
        end_ti = min(n_tiles_i, k + 1)
        
        # FIX: To avoid race conditions on 'max', we calculate the size
        # of the current wavefront and create a temporary array.
        wavefront_width = end_ti - start_ti
        wavefront_scores = np.zeros(wavefront_width, dtype=np.int32)
        
        # Parallel Loop
        for idx in prange(wavefront_width):
            ti = start_ti + idx
            tj = k - ti
            
            r_start = ti * TILE_SIZE + 1
            c_start = tj * TILE_SIZE + 1
            
            r_end = min(r_start + TILE_SIZE, rows)
            c_end = min(c_start + TILE_SIZE, cols)
            
            # Store result in specific index to avoid race condition
            wavefront_scores[idx] = process_tile(r_start, c_start, r_end, c_end, 
                                                 cols, H, seq1_arr, seq2_arr)
            
        # Reduce the scores from this wavefront safely (Sequential step)
        current_wavefront_max = 0
        for s in wavefront_scores:
            if s > current_wavefront_max:
                current_wavefront_max = s
                
        if current_wavefront_max > global_max:
            global_max = current_wavefront_max
            
    return global_max

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 sw_opt.py <sequence_length>")
        sys.exit(1)

    N = int(sys.argv[1])

    print(f"Initializing sequences (N={N})...")
    np.random.seed(42)
    # Using int8 for efficient ASCII storage (65='A', etc.)
    seq1 = np.random.choice([65, 67, 71, 84], size=N).astype(np.int8)
    seq2 = np.random.choice([65, 67, 71, 84], size=N).astype(np.int8)

    print("Compiling JIT kernels...")
    # Warmup with a small N to trigger compilation
    warmup_N = 128
    dummy_seq = np.zeros(warmup_N, dtype=np.int8)
    smith_waterman_optimized(dummy_seq, dummy_seq, warmup_N)
    print("Compilation complete. Starting Benchmark...")

    start = time.time()
    score = smith_waterman_optimized(seq1, seq2, N)
    end = time.time()

    elapsed = end - start
    print("-" * 30)
    print(f"Sequence length: {N}")
    print(f"Smith-Waterman Optimized Score: {score}")
    print(f"Execution time: {elapsed:.6f} seconds")
    print("-" * 30)

if __name__ == "__main__":
    main()
