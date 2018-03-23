import json
import time
import requests
from sseclient import SSEClient as EventSource

server_url = 'http://10.50.45.174:5000'
events_url = server_url

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
        }
        return requests.get(url = url, data = data, stream=True)

    def set_phase(self, phase):
        p = ["Red", "Yellow", "Green", "Orange"]
        print("Phase : {0}".format(p[phase]))
        self.phase = phase
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
        print("Getting rfid")
        user_rfid = "F100"  # Get this from RFID
        _ = raw_input("Insert RFID?")
        if user_rfid == self.rfid:
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
                    self.ride()
                else:
                    print("Failed response")
                    self.set_phase(CycleController.PHASE_RED)
            except:
                # TODO: Handle network error
                print("Network Error")
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
            except:
                # TODO: Handle network error
                print("Network Error")
            self.set_phase(CycleController.PHASE_RED)

    def ride(self):
        # Wait for RFID to be removed
        print("Waiting for rfid  to be removed")
        _rem = raw_input("remove?")
        # Tell server to reject ride
        data = {
            'ride_id': self.ride_id,
            'cycle_id': self.id
        }
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
        except:
            print("Network Error. Retrying after one sec.")
            time.sleep(1)

