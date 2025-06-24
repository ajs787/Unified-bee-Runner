import picamera
import time
import datetime
import os


try:
    while True:
        with picamera.PiCamera() as camera:
            camera.framerate = 3
            camera.resolution = (960, 720)
            # camera.resolution = (1440, 1080)
            
            # Start the camera preview
            camera.start_preview()
            time.sleep(5)  # Display preview for 5 seconds
            camera.stop_preview()
            
            name = str(datetime.datetime.now())
            path = ("/mnt/usb/" + name + ".h264")
            camera.start_recording(path)
            time.sleep(1200)
            camera.stop_recording()
except Exception as e:
    print(f"An error occurred: {e}")
    os.system("./mounter.sh")

