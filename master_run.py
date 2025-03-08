"""

This script is organized in chapters, so you can use the start and end flags to run specific chapters. The chapters are as follows:


Arguments:
    -h, --help
                            Show this help message and exit.
    --data_path DATA_PATH
                            Path to the data, default is ".".
    --start START
                            (unifier) Start the pipeline at the given step, default 0.
    --end END
                            (unifier) End the pipeline at the given step, default 6 (will not stop).
    --debug
                            (unifier) Print debug information and activate debug mode for logger (and other scripts), default False.
    --background-subtraction-type {MOG2,KNN}
                            (background subtraction) Background subtraction type to use, default None. Options: MOG2 or KNN.
    --width WIDTH
                            (splitting the data) Width of the images, default 960.
    --height HEIGHT
                            (splitting the data) Height of the images, default 720.
    --number-of-samples NUMBER_OF_SAMPLES
                            (sampling) The maximum number of samples to be gathered by the sampler, default 40000.
    --max-workers-video-sampling MAX_WORKERS_VIDEO_SAMPLING
                            (sampling) The number of workers to use for multiprocessing of the sampler, default 3.
    --frames-per-sample FRAMES_PER_SAMPLE
                            (sampling, splitting the data) Number of frames per sample, default 1.
    --normalize NORMALIZE
                            (sampling) Normalize the images, default True.
    --out-channels OUT_CHANNELS
                            (sampling) The number of output channels, default 1.
    --k K
                            (making the splits) Number of folds for cross-validation, default 3.
    --model MODEL
                            (making the splits) Model to use, default "alexnet".
    --fps FPS
                            (dataset creation) Frames per second, default 25.
    --starting-frame STARTING_FRAME
                            (dataset creation) Starting frame, default 1.
    --frame-interval FRAME_INTERVAL
                            (dataset creation) Space between frames, default 0.
    --test-by-time
                            (dataset creation) Create a dataset.csv based on time (instead of log files) to test correlation between daytime and class accuracy.
    --time-splits TIME_SPLITS
                            (dataset creation) If --test-by-time is used, determine the number of splits to occur.
    --files FILES
                            (dataset creation) Name of the log files to use, default "logNo.txt, logNeg.txt, logPos.txt".
    --each-video-one-class
                            (dataset creation) Treat each video as one class; a special workflow.
    --end-frame-buffer END_FRAME_BUFFER
                            (dataset creation) Number of frames to buffer at the end of the video, default 0, NOTE/TODO: only works for each frame one class and time testing, not base version
    --seed SEED
                            (making the splits) Seed for randomizing the data sets, default "01011970".
    --only_split
                            (making the splits) Finish after splitting the CSV, default False.
    --crop_x_offset CROP_X_OFFSET
                            (making the splits) Offset (in pixels) of the crop location on the original image in the x dimension, default 0.
    --crop_y_offset CROP_Y_OFFSET
                            (making the splits) Offset (in pixels) of the crop location on the original image in the y dimension, default 0.
    --training_only TRAINING_ONLY
                            (making the splits) Only generate the training set files, default False.
    --max-workers-frame-counter MAX_WORKERS_FRAME_COUNTER
                            (frame counting) Number of workers for multiprocessing of the frame counter, default 20.
    --max-workers-background-subtraction MAX_WORKERS_BACKGROUND_SUBTRACTION
                            (background subtraction) Number of workers for multiprocessing of background subtraction, default 10.
    --epochs EPOCHS
                            (training) Number of epochs to train the model, default 10.
    --gpus GPUS
                            (training) Number of GPUs to use for training, default 1.
    --gradcam-cnn-model-layer {model_a.0.0,model_a.1.0,model_a.2.0,model_a.3.0,model_a.4.0,model_b.0.0,model_b.1.0,model_b.2.0,model_b.3.0,model_b.4.0} [...]
                            (training, make validation training) Model layers for gradcam plots, default ['model_a.4.0', 'model_b.4.0'].
    --crop
                            (sampling) Crop the images to the correct size.
    --equalize-samples
                            (sampling) Equalize the samples so that each class has the same number of samples.
    --dataset-writing-batch-size DATASET_WRITING_BATCH_SIZE
                            (sampling) Batch size for writing the dataset, default 10.
    --max-threads-pic-saving MAX_THREADS_PIC_SAVING
                            (sampling) Number of threads to use for saving pictures, default 4.
    --max-batch-size-sampling MAX_BATCH_SIZE_SAMPLING
                            (sampling) Maximum batch size for sampling the video, default 5.
    --max-workers-tar-writing MAX_WORKERS_TAR_WRITING
                            (sampling) Number of workers for writing tar files, default 4.
    --y-offset Y_OFFSET
                            Y offset for the crop, default 0.
    --out-width OUT_WIDTH
                            Width of the output image, default 400.
    --out-height OUT_HEIGHT
                            Height of the output image, default 400.


Logging:
The script uses logging to provide information about the progress and any errors encountered during the execution of the pipeline.
Unified Bee Runner Pipeline Script

This script orchestrates the entire pipeline for processing and analyzing bee-related datasets. The pipeline is divided into several steps, each performing a specific task. The steps can be controlled using the `--start` and `--end` arguments, allowing users to run specific parts of the pipeline.

Chapter System:
This script is ogranized in chapters, so you can use the start and end flags to run specific chapters. The chapters are as follows:
0. Video Conversions
1. Background Subtraction
2. Dataset Creation
3. Data Splitting
4. Video Sampling
5. Model Training -> this will create slurm jobs given the number of k-folds that you have requested

- `--start`: The step with which to start the pipeline.
- `--end`: The step with which to end the pipeline.
"""

import logging
import os
import subprocess

from ArgParser import get_args

logging.basicConfig(
    format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S"
)

DIR_NAME = os.path.dirname(os.path.abspath(__file__))

try:
    args = get_args()
    logging.info("---- Starting the pipeline ----")
    path = args.data_path
    os.chdir(path)
    logging.info("---- Purging all packages ----")
    subprocess.run(
        "xargs pip uninstall -y >> /dev/null", shell=True, executable="/bin/bash"
    )

    logging.info("---- Upgrading pip ----")
    subprocess.run(
        "pip install --upgrade pip >> /dev/null", shell=True, executable="/bin/bash"
    )

    logging.info("---- Installing some requirements for the pipeline ----")
    subprocess.run(
        f"pip install -r {os.path.join(DIR_NAME, 'requirements.txt')} >> /dev/null",
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
            "(0) ---- Installing the requirements for the Video_Frame_Counter ----"
        )
        subprocess.run(
            f"pip install -r {os.path.join(DIR_NAME, 'Video_Frame_Counter/requirements.txt')} >> /dev/null",
            shell=True,
            executable="/bin/bash",
        )

        file_list = os.listdir(path)
        contains_h264 = any(".h264" in file for file in file_list)
        contains_mp4 = any(".mp4" in file for file in file_list)

        arguments = f"--max-workers {args.max_workers_frame_counter} "

        logging.info("(0) ---- Running Video Conversions Sections ----")

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

        logging.info("(0) ---- Changing Permissions for the Repository----")
        subprocess.run("chmod -R 777 . >> /dev/null 2>&1", shell=True)
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
            logging.info("(1) Starting the background subtraction")

            logging.info(
                "(1) ---- Installing the requirements for the Video_Subtractions ----"
            )
            subprocess.run(
                f"pip install -r {os.path.join(DIR_NAME, 'Video_Subtractions/requirements.txt')} >> /dev/null",
                shell=True,
            )

            arguments = (
                f" --subtractor {args.background_subtraction_type} "
                f" --max-workers {args.max_workers_background_subtraction}"
            )
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

# this is for the num_outputs arguement for the 
num_outputs = 0

if args.start <= 2 and args.end >= 2:
    logging.info("(2) Starting the dataset creation")
    try:

        logging.info(
            "(2) ---- Installing the requirements for the Dataset_Creator ----"
        )
        subprocess.run(
            f"pip install -r {os.path.join(DIR_NAME, 'Dataset_Creator/requirements.txt')} >> /dev/null",
            shell=True,
        )
        if args.test_by_time:
            logging.info(
                "Deciding the test by time, given the passing of the --test-by-time button"
            )
            arguments = (
                f" --path {path} "
                f" --counts counts.csv "  # adding these options in case they need to be changed in the future
                f" --start-frame {args.starting_frame} "
                f" --end-frame-buffer {args.end_frame_buffer} "
                f" --splits {args.time_splits} "
            )
            subprocess.run(
                f"python3 {os.path.join(DIR_NAME, 'Dataset_Creator/time_based_division.py')} {arguments} >> dataprep.log 2>&1",
                shell=True,
            )

            # outputs equals the number of splits we divide the time
            num_outputs = args.time_splits

        elif args.each_video_one_class:
            logging.info(
                "Creating a one class dataset, given the passing of the --end-frame-buffer argument"
            )
            arguments = (
                f" --path {path} "
                f" --counts counts.csv "  # adding these options in case they need to be changed in the future
                f" --start-frame {args.starting_frame} "
                f" --end-frame-buffer {args.end_frame_buffer} "
                f" --splits {args.k} "
            )
            subprocess.run(
                f"python3 {os.path.join(DIR_NAME, 'Dataset_Creator/one_class_runner.py')} {arguments} >> dataprep.log 2>&1",
                shell=True,
            )

            # outputs equal to the number of k splits
            num_outputs = args.k
        else:
            logging.info("(2) Creating a dataset.csv based on the txt files")
            
            log_list = [
                file
                for file in file_list
                if file.startswith("log") and file.endswith(".txt")
            ]
            
            logging.info(f"(2) Creating the dataset with the files: {log_list}")

            if args.files is None:
                string_log_list = ",".join(log_list).strip().replace(" ", "")
            else:
                string_log_list = args.files

            arguments = (
                f" --path {path} "
                f" --counts counts.csv "  # adding these options in case they need to be changed in the future
                f" --files '{string_log_list}' "
                f" --starting-frame {args.starting_frame} "
                f" --frame-interval {args.frame_interval} "
                f" --end-frame-buffer {args.end_frame_buffer} "
            )
            subprocess.run(
                f"python3 {os.path.join(DIR_NAME, 'Dataset_Creator/Make_Dataset.py')} {arguments} >> dataprep.log 2>&1",
                shell=True,
            )

            # the number of outputs are equal the number of logs
            num_outputs = len(log_list)
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
        logging.info("(3) Starting the data splitting")
        logging.info(
            "(3) ---- Installing the requirements for the working_bee_analysis ----"
        )
        subprocess.run(
            f"pip install -r {os.path.join(DIR_NAME, 'working_bee_analysis/requirements.txt')} >> /dev/null",
            shell=True,
        )

        arguments = (
            f" --k {args.k} "
            f" --model {args.model} "
            f" --gpus {args.gpus} "
            f" --seed {args.seed} "
            f" --width {args.width} "
            f" --height {args.height} "
            f" --path_to_file {os.path.join(DIR_NAME, 'working_bee_analysis')} "
            f" --frames_per_sample {args.frames_per_sample} "
            f" --crop_x_offset {args.crop_x_offset} "
            f" --crop_y_offset {args.crop_y_offset} "
            f" --epochs {args.epochs} "
            f" --gradcam_cnn_model_layer {' '.join(args.gradcam_cnn_model_layer)} "
            # inferred from the Dataset Creation aspects of the workflow (see: step 2)
            f" --num-outputs {num_outputs} " 
        )
        if args.only_split:
            arguments += " --only_split "
        if args.training_only:
            arguments += " --training_only "
        if args.each_video_one_class:
            arguments += " --remove-dataset-sub "
        subprocess.run(
            f"python3 {os.path.join(DIR_NAME, 'working_bee_analysis/make_validation_training.py')} {arguments} >> dataprep.log 2>&1",
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
        logging.info("(4) Starting the video sampling")

        subprocess.run(
            f"python3 {os.path.join(DIR_NAME, 'Dataset_Creator/dataset_checker.py')}",
            shell=True,
        )
        logging.info("(4) ---- Installing the requirements for the VideoSamplerRewrite")
        subprocess.run(
            f"pip install -r {os.path.join(DIR_NAME, 'VideoSamplerRewrite/requirements.txt')} >> /dev/null",
            shell=True,
        )

        subprocess.run(
            "chmod -R 777 . >> /dev/null 2>&1", shell=True
        )  # keep chmoding to make sure that the permissions are correct to sample videos
        arguments = (
            f" --frames-per-sample {args.frames_per_sample} "
            f" --number-of-samples {args.number_of_samples} "
            f" --normalize {args.normalize} "
            f" --out-channels {args.out_channels} "
            f" --max-workers {args.max_workers_video_sampling} "
            f" --dataset-writing-batch-size {args.dataset_writing_batch_size} "
            f" --max-threads-pic-saving {args.max_threads_pic_saving} "
            f" --max-workers-tar-writing {args.max_workers_tar_writing} "
            f" --max-batch-size-sampling {args.max_batch_size_sampling} "
        )
        if args.crop:
            arguments += (
                f" --crop --x-offset {args.crop_x_offset} "
                f" --y-offset {args.crop_y_offset} "
                f" --out-width {args.width} "
                f" --out-height {args.height}"
            )
        if args.debug:
            arguments += " --debug "
        if args.equalize_samples:
            arguments += " --equalize-samples "
        subprocess.run(
            f"python3 {os.path.join(DIR_NAME, 'VideoSamplerRewrite/Dataprep.py')} {arguments} >> dataprep.log 2>&1",
            shell=True,
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        raise ValueError("Something went wrong in step 4")

else:
    logging.info(
        f"Skipping step 4, given the start ({args.start}) and end ({args.end}) values"
    )

logging.info("(5) Starting the model training")
if args.start <= 5 and args.end >= 5:
    try:
        subprocess.run("chmod -R 777 . >> /dev/null 2>&1", shell=True)
        subprocess.run("./training-run.sh", shell=True)
        logging.info("Submitted executors for training")
        subprocess.run("chmod -R 777 . >> /dev/null 2>&1", shell=True)
        logging.info("Pipeline complete")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise ValueError("Something went wrong in step 5")
else:
    logging.info(
        f"Skipping step 5, given the start ({args.start}) and end ({args.end}) values"
    )
