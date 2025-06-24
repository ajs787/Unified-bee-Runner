import picamera
from picamera import PiCamera
camera=PiCamera()
from time import sleep
import time
import datetime

camera.framerate = 25
camera.resolution = (960,720)
camera.start_preview()
