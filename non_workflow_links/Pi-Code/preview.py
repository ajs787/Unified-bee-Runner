import time
import picamera
camera=picamera.PiCamera()
try:
    camera.resolution=(960,720)
    camera.start_preview()
    time.sleep(9999)
    camera.stop_preview()
finally:
    camera.close()
