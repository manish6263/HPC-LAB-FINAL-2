#!/usr/bin/env bash
# Package submission: creates a tarball with code + metadata
set -euo pipefail
TEAM=${1:-mcs242460mcs242445}
OUTPUT=submit_${TEAM}_$(date +%Y%m%d_%H%M%S).tar.gz

#remove previous tgz
rm *${TEAM}*gz
# required files
tar -czf ${OUTPUT} baseline optimized plots results Makefile collect_perf.sh final_plot.py collect_times.sh run.sh report.pdf submit.sh


echo "Created submission package: ${OUTPUT}"


echo "Please upload ${OUTPUT} in Moodle "
