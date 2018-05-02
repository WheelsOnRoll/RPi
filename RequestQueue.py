import requests, time, sys

from threading import Thread

class RequestQueue(Thread):

	def __init__(self, server_url):
		Thread.__init__(self)
		self.q = []
		self.server_url = server_url
		self.isRunning = True

	def add(self, data):
		self.q.append(data)

	def stop(self):
		self.isRunning = False

	def run(self):
		while self.isRunning:
			if len(self.q) == 0:
				time.sleep(1)
				continue
			data = self.q[0]
			try:
				self.q.remove(data)
				print("Posting Stop ride with data ", data)
				r = requests.post(url=self.server_url + '/stopride', data=data)
			except:
				print("Post failed", sys.exc_info())
				self.add(data)
				time.sleep(1)
				continue
