import picamera
import time
import datetime
import os

time.sleep(5)


try:
    while True:
        with picamera.PiCamera() as camera:
            camera.framerate = 3
            #camera.resolution = (960,720)
            camera.resolution = (1440,1080)
            name = str(datetime.datetime.now())
            path = ("/mnt/usb/" + name + ".h264")
            camera.start_recording(path)
            time.sleep(1200)
            camera.stop_recording()
except:
    os.system("./mounter.sh")
