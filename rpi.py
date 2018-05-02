import json
import os
import requests
import threading
import thread
import time

from Queue import Queue
from RequestQueue import RequestQueue
from sseclient import SSEClient as EventSource
from threading import Thread

#import smartLockProjectRfid.SPI-Py.MFRC522-python.Read
import sys
sys.path.insert(0, '/home/pi/smartLockProject/smartLockProjectRfid/SPI-Py/MFRC522-python/')
sys.path.insert(0, '/home/pi/smartLockProject/gps')

import Read2
import GPS
import motor

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
 
server_url = 'http://10.100.83.253:5000'
events_url = server_url


LED_R = 7
LED_Y = 11
LED_G = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(LED_R, GPIO.OUT)
GPIO.setup(LED_Y, GPIO.OUT)
GPIO.setup(LED_G, GPIO.OUT)

def setLED(i):
    if i == CycleController.PHASE_RED:
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_Y, GPIO.LOW)
        GPIO.output(LED_G, GPIO.LOW)
        return
    if i == CycleController.PHASE_YELLOW:
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_Y, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.LOW)
        return
    if i == CycleController.PHASE_GREEN:
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_Y, GPIO.LOW)
        GPIO.output(LED_G, GPIO.HIGH)
        return
    GPIO.output(LED_R, GPIO.LOW)
    GPIO.output(LED_Y, GPIO.LOW)
    GPIO.output(LED_G, GPIO.LOW)

class CycleController:
    """
    Class for Cycle Controller
    """

    PHASE_RED = 0
    PHASE_YELLOW = 1
    PHASE_GREEN = 2
    PHASE_ORANGE = 3

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.rfid = None
        self.ride_id = None
        self.source = None
        self.set_phase(CycleController.PHASE_RED)


    def with_requests(self, url):
        """Get a streaming response for the given event feed using requests."""
	data = {
            'id': self.id
            'ride_id': self.ride
        }
        return requests.get(url = url, data = data, stream=True)

    def set_phase(self, phase):
        p = ["Red", "Yellow", "Green", "Orange"]
        print("Phase : {0}".format(p[phase]))
        self.phase = phase
        setLED(phase)
        # TODO: Store the object to a file
        #       for later restoration.

    def init_source(self):
        response = self.with_requests(events_url + '/events')
        self.source = EventSource(response)
    
    def listen(self):
    	
     
        global server_url, event_url
        self.init_source()
        print "Listening to events"
        for event in self.source.events():
            print("Got event {0}".format(event.event))
            if event.event == 'user_request':
                response = json.loads(event.data)
                print response
                self.rfid = response["rfid"]
                self.ride_id = response["ride_id"]
                self.set_phase(CycleController.PHASE_YELLOW)
                self.source.close()
                self.source = None
                self.init_ride()
            elif event.event == 'post_ride':
                response = json.loads(event.data)
                # If user wants to continue
                if response["status"] == 'continue':
                    self.set_phase(CycleController.PHASE_YELLOW)
                    self.source.close()
                    self.source = None
                    self.init_ride()
                elif response["status"] == 'timeout' or \
                        response["status"] == 'stop':
                    self.set_phase(CycleController.PHASE_RED)
            print "Listening to events"

    def init_ride(self):
        # TODO: Start & Wait for RFID
        # If timeout , go to red phase.
        # ...
        Read2.start()
        user_rfid = Read2.get_rfid()  # Get this from RFID
        print user_rfid, self.rfid, user_rfid == self.rfid
        if int(user_rfid) == int(self.rfid):
#        print("Getting rfid")
#        user_rfid = "F100"  # Get this from RFID
#        _ = raw_input("Insert RFID?")
#        if user_rfid == self.rfid:

            # Tell server to start ride
            print("Ride Accepted")
            data = {
                'status': 'Accepted',
                'ride_id': self.ride_id,
                'cycle_id': self.id,
            }
            try:
                r = requests.post(
                    url=server_url + '/startride', data=data)
                response = json.loads(r.text)
                if response["status"] == 'success':
                    # TODO: Open the lock
                    print("Open Lock")
                    self.set_phase(CycleController.PHASE_GREEN)
                    thread.start_new_thread(motor.spin1, ())
                    self.ride()
                else:

                    print("Failed response")
                    self.set_phase(CycleController.PHASE_RED)
            except Exception as e:
                # TODO: Handle network error
                print("Network Error")
		print e
                self.set_phase(CycleController.PHASE_RED)
        else:
            # Tell server to reject ride
            print("Ride rejected")
            data = {
                'status': 'Rejected',
                'message': 'Invalid Card',
                'ride_id': self.ride_id,
                'cycle_id': self.id
            }
            try:
                r = requests.post(
                    url=server_url + '/startride', data=data)
            except Exception as e:
                # TODO: Handle network error
                print("Network Error")
                print(e)
            Read2.wait()
            Read2.stop()
            self.set_phase(CycleController.PHASE_RED)

    def ride(self):
        # Wait for RFID to be removed
        print("Waiting for rfid  to be removed")
        Read2.wait()
        Read2.stop()
        print("RFID removed")
        # _rem = raw_input("remove?")
        # Tell server to reject ride
        data = {
            'ride_id': self.ride_id,
            'cycle_id': self.id
        }
        thread.start_new_thread(motor.spin2, ())
            # r = requests.post(url= server_url + '/stopride', data=data)
        rq.add(data)
        self.set_phase(CycleController.PHASE_RED)


rq = RequestQueue(server_url)
        try:
            r = requests.post(url= server_url + '/stopride', data=data)
            print "Ride stopped."
        except:
            # TODO: Handle network error
            #       Store the ride_id and rfid in special file
            #       and send them later to server.
            print("Network Error")
            self.set_phase(CycleController.PHASE_ORANGE)

if __name__ == "__main__":
    cycle = CycleController(1, "hrishi")

    Read2.init()
    GPS.init()
    GPS.start()
    rq.start()

    print "test"
    while True:
        # Restore state
        try:
        	
       		
            p = ["Red", "Yellow", "Green", "Orange"]
            print("Restoring cycle phase {0}".format(p[cycle.phase]))
            if cycle.phase == CycleController.PHASE_GREEN:
                print("Ride restored")
                cycle.ride()
            else:
                # Phase Yellow
                if cycle.phase == CycleController.PHASE_YELLOW:
                    cycle.set_phase(CycleController.PHASE_RED)
                cycle.listen()
                
        except KeyboardInterrupt:
            Read2.stop()
            GPS.stop()
            setLED(-1)
            rq.stop()
            exit()
        except Exception as e:
	    print e
            print("Network Error. Retrying after one sec.")
            Read2.stop()
            time.sleep(1)
