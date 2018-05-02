import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)                    ## Use BOARD pin numbering.
GPIO.setup(15,GPIO.OUT)       
pwm=GPIO.PWM(15 ,100)                        ## PWM Frequency
pwm.start(5)

angle1=60
duty1= float(angle1)/10 + 2.5               ## Angle To Duty cycle  Conversion

angle2=120
duty2= float(angle2)/10 + 2.5


GPIO.setwarnings(False)



def spin1():
   pwm.ChangeDutyCycle(duty2)
	

def spin2():
   pwm.ChangeDutyCycle(duty1)

