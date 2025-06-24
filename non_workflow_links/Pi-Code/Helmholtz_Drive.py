
import RPi.GPIO as GPIO
import os
import datetime
import time

time.sleep(2)
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.OUT) ##pin 10 Input A 
GPIO.setup(14, GPIO.OUT) ##pin 8 Input B
#GPIO.setup(16, GPIO.OUT)
time.sleep(2)

GPIO.output(15, 0)  

GPIO.output(14, 0)

#freq=10 #54 kHz
#freq=100 #9.3 kHz
#freq=90 #10.2 kHz
#freq=120 #8.6 kHz
#freq=1 #112 kHz
#Time 12 Hours 43200
#Time 1.6 Hours 5760

try:
    while True:

        ### State 1: A-hi B-lo Positive field
        log = 'date +%Y%m%d_%H%M%S >> /mnt/usb/logPos.txt'
        print("BCM15 pin10 on  BCM14 pin8 off")
        os.system(log)
        GPIO.output(15, 1)
        GPIO.output(14, 0)
        #time.sleep(14400)
        #time.sleep(10)
        #time.sleep(1800)
        #time.sleep(43200)
        time.sleep(5760)

        ### State 2: A-lo B-hi Negative Field
        log = 'date +%Y%m%d_%H%M%S >> /mnt/usb/logNeg.txt'
        print("BCM15 pin10 off  BCM14 pin8 on")
        os.system(log)
        GPIO.output(15, 0)
        GPIO.output(14, 1)
        #time.sleep(14400)
        #time.sleep(10)
        #time.sleep(1800)
        #time.sleep(43200)
        time.sleep(5760)
        
        ### State 3: A-lo B-lo No Field
        log = 'date +%Y%m%d_%H%M%S >> /mnt/usb/logNo.txt'
        print("BCM15 pin10 off  BCM14 pin8 off")
        os.system(log)
        GPIO.output(14, 0)
        GPIO.output(15, 0)
        #time.sleep(14400)
        #time.sleep(10)
        #time.sleep(1800)
        #time.sleep(43200)
        time.sleep(5760)

except:
    GPIO.cleanup()
