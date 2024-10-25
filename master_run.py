"""
Unified Bee Runner Pipeline Script

This script orchestrates the entire pipeline for processing and analyzing bee-related datasets. The pipeline is divided into several steps, each performing a specific task. The steps can be controlled using the `--start` and `--end` arguments, allowing users to run specific parts of the pipeline.

Steps:
0. Video Conversion: Converts .h264 videos to .mp4 format.
1. Background Subtraction: Applies background subtraction to the videos.
2. Dataset Creation: Clones the Dataset_Creator repository and creates the dataset.
3. Data Splitting: Splits the data into training and testing sets.
4. Video Sampling: Clones the VideoSamplerRewrite repository and samples the video frames.
5. Model Training: Runs the model training script.

Chapter System:
This script is ogranized in chapters, so you can use the start and end flags to run specific chapters. The chapters are as follows:
1. Video Conversions
2. Background Subtraction
3. Dataset Creation
4. Data Splitting
5. Video Sampling
6. Model Training -> this will create slurm jobs given the number of k-folds that you have requested


- `--start`: The step with which to start the pipeline.
- `--end`: The step with which to end the pipeline.
TODO: Work to add common pitfalls
TODO: Finish implementing debugging for the pipeline
"""

import logging
import os
import subprocess

from ArgParser import get_args
from test_steps import test_step_0
from test_steps import test_step_1
from test_steps import test_step_2
from test_steps import test_step_3
from test_steps import test_step_4

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

DIR_NAME = os.path.dirname(os.path.abspath(__file__))

try:
    args = get_args()
    logging.info("---- Starting the pipeline ----")
    path = args.data_path
    os.chdir(path)
    subprocess.run("python3 -m venv venv", shell=True)
    subprocess.run(
        "source venv/bin/activate && pip install -r requirements.txt >> /dev/null",
        shell=True,
        executable="/bin/bash",
    )

    file_list = os.listdir()
    logging.info("(0) Starting the pipeline")
except Exception as e:
    logging.error(f"Error: {e}")
    raise ValueError("Something went wrong in the beginning")
# convert the videos

if args.start > args.end:
    raise ValueError("You can't have the start be higher than the end")

#  if the videos a .h264, convert to .mp4, else, just make a counts.csv
if args.start <= 0 and args.end >= 0:
    logging.info("(0) Starting the video conversions, always defaulting to .mp4")
    try:

        logging.debug(
            "---- Installing the requirements for the Video_Frame_Counter ----"
        )
        subprocess.run(
            f"pip install -r {os.path.join(DIR_NAME, 'Video_Frame_Counter/requirements.txt')} >> /dev/null",
            shell=True,
        )
        file_list = os.listdir(path)

        contains_h264 = True in [
            ".h264" in file for file in file_list
        ]  # if there is at least a single h264 file
        contains_mp4 = True in [
            ".mp4" in file for file in file_list
        ]  # if there is a single mp4 file

        arguments = f"--max-workers {args.max_workers_frame_counter}"

        logging.info("---- Running Video Conversions Sections ----")

        if contains_h264 and contains_mp4:
            raise ValueError(
                "Both types of file are in this directory, please remove one"
            )
        elif contains_h264:
            logging.info(
                "Converting .h264 to .mp4, old h264 files can be found in the h264_files folder"
            )
            subprocess.run(
                f"python3 {os.path.join(DIR_NAME, 'Video_Frame_Counter/h264tomp4.py')} {arguments} >> dataprep.log 2>&1",
                shell=True,
            )
        elif contains_mp4:
            logging.info("No conversion needed, making counts.csv")
            subprocess.run(
                f"python3 {os.path.join(DIR_NAME, 'Video_Frame_Counter/make_counts.py')} {arguments} >> dataprep.log 2>&1",
                shell=True,
            )
        else:
            raise ValueError(
                "Something went wrong with the file typing, as it seems that there are no .h264 or .mp4 files in the directory"
            )

        logging.info("---- Changing Permissions for the Repository----")
        subprocess.run("chmod -R 777 .", shell=True)
    except Exception as e:
        logging.error(f"Error: {e}")
        raise ValueError("Something went wrong in step 0")
else:
    logging.info(
        f"Skipping step 0, given the start ({args.start}) and end ({args.end}) values"
    )

if args.start <= 1 and args.end >= 1:
    logging.info("(1) Starting the background subtraction")
    try:
        if args.background_subtraction_type is not None:
            logging.info("Starting the background subtraction")

            subprocess.run(
                f"pip install -r {os.path.join(DIR_NAME,'Video_Subtractions/requirements.txt')} >> /dev/null",
                shell=True,
            )

            arguments = f"--subtractor {args.background_subtraction_type} --max-workers {args.max_workers_background_subtraction}"
            subprocess.run(
                f"python3 {os.path.join(DIR_NAME, 'Video_Subtractions/Convert.py')} {arguments} >> dataprep.log 2>&1",
                shell=True,
            )

        else:
            logging.info("No background subtraction type given, skipping this step")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise ValueError("Something went wrong in step 1")
else:
    logging.info(
        f"Skipping step 1, given the start ({args.start}) and end ({args.end}) values"
    )

if args.start <= 2 and args.end >= 2:
    logging.info("(2) Starting the dataset creation")
    try:
        # finds the logs, which should be named either logNo, logPos, or logNeg
        log_list = [
            file.strip()
            for file in os.listdir()
            if file.strip() == "logNo.txt"
            or file.strip() == "logPos.txt"
            or file.strip() == "logNeg.txt"
        ]
        logging.info(f"Creating the dataset with the files: {log_list}")

        subprocess.run(
            f"pip install -r {os.path.join(DIR_NAME, 'Dataset_Creator/requirements.txt')} >> /dev/null",
            shell=True,
        )
        if args.files is None:
            string_log_list = ",".join(log_list).strip().replace(" ", "")
        else:
            string_log_list = args.files

        arguments = f"--files '{string_log_list}' --starting-frame {args.starting_frame} --frame-interval {args.frame_interval}"
        subprocess.run(
            f"python3 {os.path.join(DIR_NAME, 'Dataset_Creator/Make_Dataset.py')} {arguments} >> dataprep.log 2>&1",
            shell=True,
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        raise ValueError("Something went wrong in step 2")
else:
    logging.info(
        f"Skipping step 2, given the start ({args.start}) and end ({args.end}) values"
    )

logging.info("(3) Splitting up the data")
if args.start <= 3 and args.end >= 3:
    try:
        # !!! VERY IMPORTANT !!!, change the path_to_file to the path of the file that was created in the last step

        subprocess.run(
            f"pip install -r {os.path.join(DIR_NAME, 'working_bee_analysis/requirements.txt')} >> /dev/null",
            shell=True,
        )

        arguments = f"--k {args.k} --model {args.model} --gpus {args.gpus} --seed {args.seed} --width {args.width} --height {args.height} --path_to_file {os.path.join(DIR_NAME,'working_bee_analysis')} --frames_per_sample {args.frames_per_sample} --crop_x_offset {args.crop_x_offset} --crop_y_offset {args.crop_y_offset} --epochs {args.epochs}"
        if args.only_split:
            arguments += " --only_split"
        if args.training_only:
            arguments += " --training_only"
        subprocess.run(
            f"python3 {os.path.join(DIR_NAME, 'working-bee-analysis/make_validation_training.py')} {arguments} >> dataprep.log 2>&1",
            shell=True,
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        raise ValueError("Something went wrong in step 3")
else:
    logging.info(
        f"Skipping step 3, given the start ({args.start}) and end ({args.end}) values"
    )

logging.info("(4) Starting the tar sampling")
if args.start <= 4 and args.end >= 4:
    try:
        subprocess.run(
            f"python3 {os.path.join(DIR_NAME, 'Dataset_Creator/dataset_checker.py')}",
            shell=True,
        )

        subprocess.run(
            f"pip install -r {os.path.join(DIR_NAME, 'VideoSamplerRewrite/requirements.txt')} >> /dev/null",
            shell=True,
        )

        subprocess.run(
            "chmod -R 777 . >> /dev/null 2>&1", shell=True
        )  # keep chmoding to make sure that the permissions are correct to sample videos
        arguments = f"--frames-per-sample {args.frames_per_sample} --number-of-samples {args.number_of_samples} --normalize {args.normalize} --out-channels {args.out_channels} --max-workers {args.max_workers_video_sampling}"
        if args.crop:
            arguments += f" --crop --x-offset {args.crop_x_offset} --y-offset {args.crop_y_offset} --out-width {args.width} --out-height {args.height}"
        if args.debug:
            arguments += " --debug"
        subprocess.run(
            f"python3 {os.path.join(DIR_NAME, 'VideoSamplerRewrite/Dataprep.py')} {arguments} >> dataprep.log 2>&1",
            shell=True,
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        raise ValueError("Something went wrong in step 4")
    finally:
        test_step_4("VideoSamplerRewrite")

else:
    logging.info(
        f"Skipping step 4, given the start ({args.start}) and end ({args.end}) values"
    )

logging.info("(5) Starting the model training")
if args.start <= 5 and args.end >= 5:
    try:
        subprocess.run("chmod -R 777 . >> dataprep.log 2>&1", shell=True)
        subprocess.run("./training-run.sh", shell=True)
        subprocess.run("chmod -R 777 . >> dataprep.log 2>&1", shell=True)

        logging.info("Pipeline complete, training is occuring")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise ValueError("Something went wrong in step 5")
else:
    logging.info(
        f"Skipping step 5, given the start ({args.start}) and end ({args.end}) values"
    )
