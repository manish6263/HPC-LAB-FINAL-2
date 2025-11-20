// #include <stdio.h>
// #include <stdlib.h>
// #include <string.h>
// #include <time.h>
// #include <omp.h>
// #include <immintrin.h> // Required for SIMD if we added explicit intrinsics

// #define MAX(A,B) ((A) > (B) ? (A) : (B))
// #define MATCH     2
// #define MISMATCH -1
// #define GAP      -2
// #define TILE_SIZE 128 // Optimizing for L1/L2 Cache size

// void generate_sequence(char *seq, int n) {
//     const char alphabet[] = "ACGT";
//     for (int i = 0; i < n; i++)
//         seq[i] = alphabet[rand() % 4];
//     seq[n] = '\0';
// }

// // Compute a single tile sequentially
// // Because the tile is small (128x128), this fits entirely in L1 cache.
// void process_tile(int start_i, int start_j, int end_i, int end_j, 
//                   int len1, int len2, const char *seq1, const char *seq2, 
//                   int **H, int *local_max) {
    
//     int max_score = 0;
    
//     for (int i = start_i; i <= end_i; i++) {
//         for (int j = start_j; j <= end_j; j++) {
//             int match_score = (seq1[i - 1] == seq2[j - 1]) ? MATCH : MISMATCH;
            
//             // Standard recurrence
//             int diag = H[i - 1][j - 1] + match_score;
//             int up   = H[i - 1][j] + GAP;
//             int left = H[i][j - 1] + GAP;
            
//             int score = MAX(0, MAX(diag, MAX(up, left)));
//             H[i][j] = score;
            
//             if (score > max_score) max_score = score;
//         }
//     }
    
//     // Update global max score thread-safely later, or strictly local here
//     if (max_score > *local_max) {
//         *local_max = max_score;
//     }
// }

// int smith_waterman_tiled(const char *seq1, const char *seq2, int len1, int len2) {
//     // Allocate full matrix (O(N^2) space)
//     // Note: For extremely large N, we would need O(N) space blocking, 
//     // but for this assignment's expected constraints, this highlights parallelism best.
//     int **H = malloc((len1 + 1) * sizeof(int *));
//     for (int i = 0; i <= len1; i++)
//         H[i] = calloc(len2 + 1, sizeof(int));

//     int global_max = 0;
    
//     // Calculate number of tiles
//     int n_tiles_i = (len1 + TILE_SIZE - 1) / TILE_SIZE;
//     int n_tiles_j = (len2 + TILE_SIZE - 1) / TILE_SIZE;
    
//     // Wavefront iteration over TILES (not cells)
//     // k is the wavefront index (anti-diagonal of tiles)
//     for (int k = 0; k < n_tiles_i + n_tiles_j - 1; k++) {
        
//         // Parallelize processing of tiles in the current wavefront
//         #pragma omp parallel reduction(max:global_max)
//         {
//             int local_max = 0;
            
//             #pragma omp for schedule(dynamic)
//             for (int ti = 0; ti < n_tiles_i; ti++) {
//                 int tj = k - ti;
                
//                 // Check if tile indices are valid
//                 if (tj >= 0 && tj < n_tiles_j) {
                    
//                     int start_i = ti * TILE_SIZE + 1;
//                     int start_j = tj * TILE_SIZE + 1;
                    
//                     int end_i = (ti + 1) * TILE_SIZE;
//                     if (end_i > len1) end_i = len1;
                    
//                     int end_j = (tj + 1) * TILE_SIZE;
//                     if (end_j > len2) end_j = len2;
                    
//                     process_tile(start_i, start_j, end_i, end_j, 
//                                  len1, len2, seq1, seq2, H, &local_max);
//                 }
//             }
            
//             if (local_max > global_max) global_max = local_max;
//         }
//     }

//     for (int i = 0; i <= len1; i++) free(H[i]);
//     free(H);

//     return global_max;
// }

// int main(int argc, char **argv) {
//     if (argc < 2) {
//         fprintf(stderr, "Usage: %s <sequence_length>\n", argv[0]);
//         return 1;
//     }

//     int N = atoi(argv[1]);
//     srand(42);

//     char *seq1 = malloc((N + 1) * sizeof(char));
//     char *seq2 = malloc((N + 1) * sizeof(char));

//     generate_sequence(seq1, N);
//     generate_sequence(seq2, N);

//     struct timespec start, end;
//     clock_gettime(CLOCK_MONOTONIC, &start);

//     // Call the TILED version
//     int score = smith_waterman_tiled(seq1, seq2, N, N);

//     clock_gettime(CLOCK_MONOTONIC, &end);

//     double elapsed = (end.tv_sec - start.tv_sec);
//     elapsed += (end.tv_nsec - start.tv_nsec) / 1000000000.0;
    
//     printf("Sequence length: %d\n", N);
//     printf("Smith-Waterman optimized score: %d\n", score);
//     printf("Execution time: %.6f seconds\n", elapsed);

//     free(seq1);
//     free(seq2);
//     return 0;
// }

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <omp.h>

#define MAX(A,B) ((A) > (B) ? (A) : (B))
#define MATCH     2
#define MISMATCH -1
#define GAP      -2
#define TILE_SIZE 128 

void generate_sequence(char *seq, int n) {
    const char alphabet[] = "ACGT";
    for (int i = 0; i < n; i++)
        seq[i] = alphabet[rand() % 4];
    seq[n] = '\0';
}

// Process tile using 1D memory access
void process_tile(int start_i, int start_j, int end_i, int end_j, 
                  int len1, int len2, const char *seq1, const char *seq2, 
                  int *H, int *local_max) {
    
    int max_score = 0;
    int cols = len2 + 1; // Width of the matrix row

    for (int i = start_i; i <= end_i; i++) {
        // Pre-calculate row offsets to avoid multiplication in inner loop
        int curr_row_offset = i * cols;
        int prev_row_offset = (i - 1) * cols;

        for (int j = start_j; j <= end_j; j++) {
            int match_score = (seq1[i - 1] == seq2[j - 1]) ? MATCH : MISMATCH;
            
            // Access 1D array: H[row * width + col]
            int diag = H[prev_row_offset + (j - 1)] + match_score;
            int up   = H[prev_row_offset + j] + GAP;
            int left = H[curr_row_offset + (j - 1)] + GAP;
            
            int score = MAX(0, MAX(diag, MAX(up, left)));
            H[curr_row_offset + j] = score;
            
            if (score > max_score) max_score = score;
        }
    }
    
    if (max_score > *local_max) {
        *local_max = max_score;
    }
}

int smith_waterman_tiled(const char *seq1, const char *seq2, int len1, int len2) {
    // 1. Allocate FLAT 1D Memory (Use long long to prevent overflow on size calc)
    // This is much lighter on RAM and faster for the CPU
    size_t total_cells = (size_t)(len1 + 1) * (size_t)(len2 + 1);
    int *H = calloc(total_cells, sizeof(int));
    if (!H) {
        fprintf(stderr, "Failed to allocate memory for %dx%d matrix\n", len1, len2);
        exit(1);
    }

    int global_max = 0;
    
    int n_tiles_i = (len1 + TILE_SIZE - 1) / TILE_SIZE;
    int n_tiles_j = (len2 + TILE_SIZE - 1) / TILE_SIZE;
    
    for (int k = 0; k < n_tiles_i + n_tiles_j - 1; k++) {
        #pragma omp parallel reduction(max:global_max)
        {
            int local_max = 0;
            #pragma omp for schedule(dynamic)
            for (int ti = 0; ti < n_tiles_i; ti++) {
                int tj = k - ti;
                if (tj >= 0 && tj < n_tiles_j) {
                    int start_i = ti * TILE_SIZE + 1;
                    int start_j = tj * TILE_SIZE + 1;
                    int end_i = (ti + 1) * TILE_SIZE;
                    if (end_i > len1) end_i = len1;
                    int end_j = (tj + 1) * TILE_SIZE;
                    if (end_j > len2) end_j = len2;
                    
                    process_tile(start_i, start_j, end_i, end_j, 
                                 len1, len2, seq1, seq2, H, &local_max);
                }
            }
            if (local_max > global_max) global_max = local_max;
        }
    }

    free(H);
    return global_max;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <sequence_length>\n", argv[0]);
        return 1;
    }

    int N = atoi(argv[1]);
    srand(42);

    char *seq1 = malloc((N + 1) * sizeof(char));
    char *seq2 = malloc((N + 1) * sizeof(char));

    generate_sequence(seq1, N);
    generate_sequence(seq2, N);

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    int score = smith_waterman_tiled(seq1, seq2, N, N);

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec);
    elapsed += (end.tv_nsec - start.tv_nsec) / 1000000000.0;
    
    printf("Sequence length: %d\n", N);
    printf("Smith-Waterman optimized score: %d\n", score);
    printf("Execution time: %.6f seconds\n", elapsed);

    free(seq1);
    free(seq2);
    return 0;
}