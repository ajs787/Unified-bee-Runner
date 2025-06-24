import picamera
from picamera import PiCamera
camera=PiCamera()
from time import sleep
import time
import datetime

camera.framerate = 25
camera.resolution = (960,720)
camera.start_preview()
sleep(10000)
camera.stop_preview()
while True:
#    with picamera.PiCamera() as camera:
        camera.framerate = 25
        camera.resolution = (960,720)
        name = str(datetime.datetime.now())
        #name = str(time.strfttime("%m%d%Y-%H%M%S"))
        path = ("/mnt/usb/" + name + ".h264")
        camera.vflip=1
        #camera.start_preview()
        camera.start_recording(path)
        print("it is recording! :)")
        sleep(1200)
        camera.stop_recording()
        print("it stopped recording! :)")
        #camera.stop_preview()
