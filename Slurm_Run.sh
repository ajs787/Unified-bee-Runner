#!/bin/bash

echo "submitting slurm job. Remember to edit the Unifier_Run.sh if you want to make changes"

sbatch \
  -n 4 \
  -c 6 -G 1 --mem=300G \
  --time=28800 \
  -o dataprep.log \
  Unified-bee-Runner/Unifier_Run.sh

echo "submitted"
