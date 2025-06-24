import RPi.GPIO as GPIO
import os
import datetime
import time

time.sleep(2)
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
time.sleep(2)




try:
    while True:

        ### State 1: A-hi B-lo Positive field
        #log = 'date +%Y%m%d_%H%M%S >> /mnt/usb/logPos.txt'
        #os.system(log)
        #print("BCM pin 15 on")
        GPIO.output(15, 1)
        #time.sleep(60*5)


        ### State 2: A-lo B-lo No Field
        #log = 'date +%Y%m%d_%H%M%S >> /mnt/usb/logNo.txt'
        #print("15 pin off")
        #os.system(log)
        GPIO.output(15, 0)
       #time.sleep(60*5)
        

except:
    GPIO.cleanup()
