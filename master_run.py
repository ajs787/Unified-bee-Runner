import argparse
import os
import logging
import subprocess

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

try:

    description = """
    Runs the pipeline that runs the model on the data
    \n
    This programs expects the log files to be named of the form logNo.txt, logPos.txt, logNeg.txt
    \n
    This script automatically converts the videos to .mp4, and then runs the pipeline on the data, type of video can either be mp4 or h264
    \n
    This program also expects that you are running this on the ilab servers, with the anaconda environment of
    /koko/system/anaconda/envs/python38/bin:$PATH and /koko/system/anaconda/envs/python39/bin:$PATH
    \n\n\n\n\n\n\n\n



    One file to rule them all,
    one file to find them,
    One file to bring them all,
    and in the data directory train them;
    In the Land of ilab where the shadows lie.
    """

    logging.info("(0) Starting the pipeline")

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--data_path",
        type=str,
        help='Path to the data, default "."',
        default=".",
        required=False,
    )
    parser.add_argument(
        "--start",
        type=int,
        help="(unifier)Start the pipeline at the given step, default 0",
        default=0,
        required=False,
    )
    parser.add_argument(
        "--stop",
        type=int,
        help="(unifier)Stop the pipeline at the given step, default -1 (will not stop)",
        default=-1,
        required=False,
    )
    # for background subtraction
    parser.add_argument(
        "--background-subtraction-type",
        choices=["MOG2", "KNN"],
        required=False,
        default=None,
        type=str,
        help="(background subtraction)Background subtraction type to use, default None",
    )
    # for make_validation_training
    parser.add_argument(
        "--width",
        type=int,
        help="(splitting the data) Width of the images, default 960",
        default=960,
        required=False,
    )
    parser.add_argument(
        "--height",
        type=int,
        help="(splitting the data) Height of the images, default 720",
        default=720,
        required=False,
    )

    # for sampling
    parser.add_argument(
        "--number-of-samples",
        type=int,
        help="(sampling)the number of samples max that will be gathered by the sampler, defalt=1000",
        default=1000,
    )
    parser.add_argument(
        "--max-workers-video-sampling",
        type=int,
        help="(sampling)The number of workers to use for the multiprocessing of the sampler, default=15",
        default=15,
    )
    parser.add_argument(
        "--frames-per-sample",
        type=int,
        help="(sampling, splitting the data)The number of frames per sample, default=1",
        default=1,
    )
    parser.add_argument(
        "--normalize",
        type=bool,
        help="(sampling) normalize the images, default=True",
        default=True,
    )
    parser.add_argument(
        "--out-channels",
        type=int,
        help="(sampling) The number of output channels, default=1",
        default=1,
    )
    parser.add_argument(
        "--k",
        type=int,
        help="(making the splits) Number of folds for cross validation, default 3",
        default=3,
        required=False,
    )
    parser.add_argument(
        "--model",
        type=str,
        help="(making the splits) model to use, default alexnet",
        default="alexnet",
        required=False,
    )

    # CREATING THE DATASET
    parser.add_argument(
        "--files",
        type=str,
        help="(dataset creation) name of the log files that one wants to use, default logNo.txt, logNeg.txt, logPos.txt",
        default="logNo.txt, logPos.txt, logNeg.txt",
    )
    parser.add_argument(
        "--fps",
        type=int,
        help="(dataset creation) frames per second, default 25",
        default=25,
    )
    parser.add_argument(
        "--starting-frame",
        type=int,
        help="(dataset creation) starting frame, default 1",
        default=1,
    )
    parser.add_argument(
        "--frame-interval",
        type=int,
        help="(dataset creation) space between frames, default 0",
        default=0,
    )

    parser.add_argument(
        "--seed",
        type=str,
        default="01011970",
        help="Seed to use for randominizing the data sets, default: 01011970",
    )

    # ? not used RN
    # parser.add_argument(
    #     "--training-script-file",
    #     type=str,
    #     required=False,
    #     default="training-run",
    #     help="Name for the training script file, default: training-run",
    # )

    args = parser.parse_args()

    # getting the path working
    subprocess.run(
        "export PATH=/koko/system/anaconda/envs/python38/bin:$PATH", shell=True
    )

    path = args.data_path
except Exception as e:
    logging.error(f"Error: {e}")
    raise "Something went wrong in the beginning"
# convert the videos
logging.info("(0) Starting the video conversions, always defaulting to .mp4")

#  if the videos a .h264, convert to .mp4
try:
    os.chdir(path)
    subprocess.run(
        "git clone https://github.com/Elias2660/Video_Frame_Counter.git >> clones.log 2>&1",
        shell=True,
    )
    file_list = os.listdir(path)
    contains_h264 = True in [".h264" in file for file in file_list]
    contains_mp4 = True in [".mp4" in file for file in file_list]
    if contains_h264 and contains_mp4:
        raise "Both types of file are in this directory, please remove one"
    elif contains_h264:
        logging.info(
            "Converting .h264 to .mp4, old h264 files can be found in the h264_files folder"
        )
        subprocess.run(
            "python Video_Frame_Counter/h264tomp4.py >> conversion.log 2>&1", shell=True
        )
    elif contains_mp4:
        logging.info("No conversion needed, making counts.csv")
        subprocess.run(
            "python Video_Frame_Counter/make_counts.py >> conversion.log 2>&1",
            shell=True,
        )
    else:
        raise "Something went wrong with the file typing, as it seems that there are no .h264 or .mp4 files in the directory"
except Exception as e:
    logging.error(f"Error: {e}")
    raise "Something went wrong in step 1"


logging.info("(1) Starting the background subtraction")
try:
    # TODO create the background subtraction
    if args.background_subtraction_type is not None:
        logging.info("Starting the background subtraction")
    else:
        logging.info("No background subtraction type given, skipping this step")
except Exception as e:
    logging.error(f"Error: {e}")
    raise "Something went wrong in step 2"

logging.info("(2) Starting the data set creation")
try:
    log_list = [file.strip() for file in os.listdir(path) if "log" in file]
    subprocess.run(
        "git clone https://github.com/Elias2660/Dataset_Creator.git >> clones.log 2>&1",
        shell=True,
    )
    subprocess.run(
        f"python Dataset_Creator/Make_Dataset.py --files {','.join(log_list).strip().replace(' ', '')} --starting-frame {args.starting_frame} --frame-interval {args.frame_interval} >> make_dataset.log 2>&1",
        shell=True,
    )
except Exception as e:
    logging.error(f"Error: {e}")
    raise "Something went wrong in step 3"

logging.info("(3) Splitting up the data")
try:
    # !!! VERY IMPORTANT !!!, change the path_to_file to the path of the file that was created in the last step
    BEE_ANALYSIS_CLONE = "https://github.com/Elias2660/working_bee_analysis.git"
    subprocess.run(f"git clone {BEE_ANALYSIS_CLONE} >> clones.log 2>&1", shell=True)
    dir_name = BEE_ANALYSIS_CLONE.split(".")[0].strip().split("/")[-1].strip()
    subprocess.run(
        f"python {dir_name}/make_validation_train.py --k {args.k} --model {args.model} --seed {args.seed} --width {args.width} --path_to_file {dir_name} >> dataset_split.log 2>&1",
        shell=True,
    )
except Exception as e:
    logging.error(f"Error: {e}")
    raise "Something went wrong in step 4"

logging.info("(4) Starting the tar sampling")
try:
    subprocess.run("python Dataset_Creater/dataset_checker.py", shell=True)
    subprocess.run(
        f"git clone https://github.com/Elias2660/VideoSamplerRewrite.git >> clones.log 2>&1",
        shell=True,
    )
    subprocess.run(
        f"python VideoSamplerRewrite/Dataprep.py --frames-per-sample {args.frames_per_sample} --number-of-samples {args.number_of_samples} --normalize {args.normalize} --out-channels {args.out_channels} --max-workers {args.max_workers_video_sampling} >> dataprep.log 2>&1",
        shell=True,
    )
except Exception as e:
    logging.error(f"Error: {e}")
    raise "Something went wrong in step 4"

logging.info("(5) Starting the model training")
try:
    subprocess.run("chmod -R 777 . >> chmoding.log >> 2>&1", shell=True)
    subprocess.run(f"bash training-run.sh")
    logging.info("Pipeline complete, training is occuring")
except Exception as e:
    logging.error(f"Error: {e}")
    raise "Something went wrong in step 5"
