import argparse

def get_args() :
    description = """
    Runs the pipeline that runs the model on the data.
    \n
    This programs expects the log files to be named of the form logNo.txt, logPos.txt, logNeg.txt.
    \n
    This script automatically converts the videos to .mp4, and then runs the pipeline on the data, type of video can either be mp4 or h264.
    \n
    This program also expects that you are running this on the ilab servers, with the anaconda environment of
    /koko/system/anaconda/envs/python38/bin:$PATH and /koko/system/anaconda/envs/python39/bin:$PATH.
    \n\n\n\n\n\n\n\n
    """
    poem = """    One file to rule them all,
    one file to find them,
    One file to bring them all,
    and in the data directory train them;
    In the Land of ilab where the shadows lie."""

    # truncating the log file

    parser = argparse.ArgumentParser(description=description, epilog=poem)
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
        "--end",
        type=int,
        help="(unifier)end the pipeline at the given step, default 6 (will not stop)",
        default=6,
        required=False,
    )
    # for background subtraction
    parser.add_argument(
        "--background-subtraction-type",
        choices=["MOG2", "KNN"],
        required=False,
        default=None,
        type=str,
        help="(background subtraction)Background subtraction type to use, default None, you can either choose MOG2 or KNN",
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
        help="(sampling)the number of samples max that will be gathered by the sampler, defalt=40000",
        default=40000,
    )
    parser.add_argument(
        "--max-workers-video-sampling",
        type=int,
        help="(sampling)The number of workers to use for the multiprocessing of the sampler, default=15",
        default=10,
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
        help="(making the splits) Seed to use for randominizing the data sets, default: 01011970",
    )
    parser.add_argument(
        "--only_split",
        required=False,
        default=False,
        action="store_true",
        help="(making the splits) Set to finish after splitting the csv, default: False",
    )
    parser.add_argument(
        "--crop_x_offset",
        type=int,
        required=False,
        default=0,
        help="(making the splits) The offset (in pixels) of the crop location on the original image in the x dimension, default 0",
    )
    parser.add_argument(
        "--crop_y_offset",
        type=int,
        required=False,
        default=0,
        help="(making the splits) The offset (in pixels) of the crop location on the original image in the y dimension, default 0",
    )
    parser.add_argument(
        "--training_only",
        type=bool,
        required=False,
        default=False,
        help="(making the splits) only generate the training set files, default: False",
    )
    parser.add_argument(
        "--files",
        type=str,
        help="(dataset creation) name of the log files that one wants to use, default logNo.txt, logNeg.txt, logPos.txt",
        default=None,
        required=False,
    )
    parser.add_argument(
        "--max-workers-frame-counter",
        type=int,
        help="(frame counting) The number of workers to use for the multiprocessing of the frame counter, default=20",
        default=20,
        required=False,
    )
    
    parser.add_argument(
        "--max-workers-background-subtraction",
        type=int,
        help="(background subtraction) The number of workers to use for the multiprocessing of the background subtraction, default=10",
        default=10,
        required=False,
    )
    args = parser.parse_args()
    return args