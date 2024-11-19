#!/bin/bash

echo "submitting slurm job. Remember to edit the Unifier_Run.sh if you want to make changes"

sbatch \
    -n 8 \
    -c 12\
    -G 1\
    --mem=200G \
    -o dataprep.log \
    Unified-bee-Runner/Unifier_Run.sh

echo "submitted"
