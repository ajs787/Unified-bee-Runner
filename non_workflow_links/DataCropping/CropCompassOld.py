import os
import logging
import argparse
import numpy as np
import cv2
import concurrent.futures
import re
import subprocess
from multiprocessing import freeze_support

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")
# logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description="Create counts.csv file")

parser.add_argument(
    "--path",
    type=str,
    help="Path to the directory containing the video files",
    default="."
)
parser.add_argument(
    "--max-workers", type=int, help="Number of processes to use", default=20
)
args = parser.parse_args()
# original_path = os.path.join(os.getcwd(), args.path)


def process_vids(original_path: str, file: str):
    logging.info(original_path)
    path = os.path.join(original_path, "old", file) # original_path, old created earlier
    logging.info(f"Capture to Path {file} about to be established")

    cap = cv2.VideoCapture(path)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    writer = cv2.VideoWriter(
        file,
        cv2.VideoWriter_fourcc(*"mp4v"),
        int(cap.get(cv2.CAP_PROP_FPS)),
        (width, height),
    )
    logging.info(f"Writer to Path {file} established")
    try:
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if count % 1500 == 0:
                logging.info(f"Frame {count} read from {file}")
            if not ret:
                break

            mask = np.zeros((int(height), int(width), 3), dtype=np.uint8)
            # Flip the mask color to white
            mask.fill(255)

            color = (1, 1, 1)

            start_point_1 = ((3*width)//4, height // 3)
            end_point_1 = (int(width), (4 * height) // 5) # all of width because of shadow

            mask = cv2.rectangle(mask, start_point_1, end_point_1, color, -1)

            result = cv2.bitwise_and(frame, mask)
            writer.write(result)
            count += 1

        cap.release()
        logging.info(f"Capture to Path {path} released")
        writer.release()
        logging.info(f"Writer to Path {file} released")
    except Exception as e:
        logging.error(f"Error in counting frames for {file} with error {e}")
        cap.release()


if __name__ == "__main__":
    freeze_support()
    try:
        # subprocess.run("rm -rf old", shell=True)
        subprocess.run("mkdir old", shell=True)
        src_path = os.path.join(args.path, "*.mp4")
        dest_path = os.path.join(args.path, "old")
        command = f"mv {src_path} {dest_path}"
        subprocess.run(command, shell=True)
        file_list = os.listdir(os.path.join(args.path, "old"))
        # only keep unique mp4 files
        file_list = list(set([file for file in file_list if re.search(r".mp4$", file)]))
        logging.debug(f"File List: {file_list}")
    except Exception as e:
        logging.error(f"Error in getting file list with error {e}")

    try:
        logging.debug(args.path)
        logging.info(f"File List: {file_list}")
    
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.max_workers
        ) as executor:
            logging.debug(f"Executor established")
            futures = [
                executor.submit(process_vids, args.path, file)
                for file in file_list
            ]
            concurrent.futures.wait(futures)
            logging.debug(f"Executor mapped")
    except Exception as e:
        logging.error(f"Error in creating counts.csv with error {e}")
