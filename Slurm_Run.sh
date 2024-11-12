#!/bin/bash

echo "submitting slurm job. Remember to edit the Unifier_Run.sh if you want to make changes"

sbatch \
    -c 8 \
    -n 4 \
    -G 1 \
    -x ilab4 \
    Unified-bee-Runner/Unifier_Run.sh

echo "submitted"
