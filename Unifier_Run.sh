#!/bin/bash

# QUICKSTART OPTIONS, or some stuff that could be interesting to test out
# --width: width of the video
# --height: height of the video
# --number-of-samples: number of samples to take by the video sampler max for each line in the separated dataset
# --frames-per-sample: number of frames to take for each sample
# --start: the step with which to start
# --end: the step with which to end
# --gpus: the number of gpus to use

# Additionally, you can run the following command to get the help menu
# python Unified-bee-Runner/master_run.py --help

# restrict the number of subthreads because all our commands use multiprocessing
# this is to prevent the system from running out of memory
# https://stackoverflow.com/questions/30791550/limit-number-of-threads-in-numpy

export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1

# Chapter System:
# This script is organized in chapters, so you can use the start and end flags to run specific chapters. The chapters are as follows:
# 0. Video Conversions
# 1. Background Subtraction
# 2. Dataset Creation
# 3. Data Splitting
# 4. Video Sampling
# 5. Model Training -> this will create slurm jobs given the number of k-folds that you have requested

# make sure we're all using the same python
# a big problems with .bashrcs lol
export PATH="/usr/bin/python3:$PATH"

cd Unified-bee-Runner || exit
git submodule update --init --recursive
cd ..

python3 -m venv venv
source venv/bin/activate

# if you are training with each video being a separate class,
# use this flag: --each-video-one-class to make it work

python3 Unified-bee-Runner/master_run.py \
  --equalize-samples \
  --height 720 \
  --width 960 \
  --number-of-samples 100 --max-workers-video-sampling 2 \
  --frames-per-sample 5 \
  --gpus 2 >>dataprep.log 2>&1
