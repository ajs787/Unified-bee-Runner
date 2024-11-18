#!/bin/bash

echo "submitting slurm job. Remember to edit the Unifier_Run.sh if you want to make changes"

sbatch \
    -c 10 \
    -n 8 \
    -G 1 \
    -o dataprep.log \
    Unified-bee-Runner/Unifier_Run.sh

echo "submitted"
