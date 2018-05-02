import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

ste = 15
dirc = 16

GPIO.setmode(GPIO.BOARD)

GPIO.setup(ste, GPIO.OUT)

GPIO.setup(dirc, GPIO.OUT)

def motor(step,x):

    GPIO.output(dirc,x)

    count=0
    delay = 0.0012
    while(count<step):
        GPIO.output(ste,1)
        time.sleep(delay)
        GPIO.output(ste,0)
        time.sleep(delay)
        count+=1


t = 50

def spin1():
    motor(t, 1)

def spin2():
    motor(t, 0)
