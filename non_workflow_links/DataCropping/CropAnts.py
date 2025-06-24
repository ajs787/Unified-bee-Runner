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
    path = os.path.join(original_path, file)
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

            start_point_1 = (0, 0)
            end_point_1 = (width // 6, height)

            mask = cv2.rectangle(mask, start_point_1, end_point_1, color, -1)

            start_point_2 = (int(width // 2), 0)
            end_point_2 = (int(width), int(height))
            
            mask = cv2.rectangle(mask, start_point_2, end_point_2, color, -1)

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
        command = f"ls {args.path} | grep -E '.mp4$|.h264$'"
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        file_list = sorted(
            [ansi_escape.sub("", line) for line in result.stdout.splitlines()]
        )
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
