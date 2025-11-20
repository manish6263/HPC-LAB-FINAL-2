# # Compiler and flags
# CC = gcc
# # Use optimizations: -O3, -march=native (for AVX etc.), and -fopenmp (for OpenMP)
# CFLAGS = -O3 -march=native -Wall
# LDFLAGS = 

# # Specific flags for the parallel optimized version
# OPT_CFLAGS = $(CFLAGS) -fopenmp
# OPT_LDFLAGS = $(LDFLAGS) -fopenmp

# # --- Targets ---

# all: baseline/sw_baseline optimized/sw_opt

# # Rule for the baseline C code
# baseline/sw_baseline: baseline/sw_baseline.c
# 	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

# # Rule for the optimized C code
# optimized/sw_opt: optimized/sw_opt.c
# 	$(CC) $(OPT_CFLAGS) $< -o $@ $(OPT_LDFLAGS)

# clean:
# 	rm -f baseline/sw_baseline optimized/sw_opt

# Python Makefile
# No compilation required for Python/Numba, but we provide 'clean' to remove artifacts.

all:
	@echo "Python project selected. No compilation necessary."
	@echo "Ensure dependencies are installed: pip install numpy numba"

clean:
	rm -rf baseline/__pycache__
	rm -rf optimized/__pycache__
	rm -f results/*.csv