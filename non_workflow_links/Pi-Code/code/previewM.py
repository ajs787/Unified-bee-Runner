import time
import picamera
camera=picamera.PiCamera()
try:
    camera.resolution=(1440,1080)
#    camera.awb_mode='off'
#    camera.exposure_mode='auto'
#   camera.brightness=60
    #camera.shutter_speed =25

    camera.iso=800
    #camera.exposure_compensation=-25
    camera.start_preview()
    time.sleep(9999)
    camera.stop_preview()
finally:
    camera.close()
