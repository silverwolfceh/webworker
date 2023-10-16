import threading
import time
import random

# An abstract class for implement worker threads
class webworker(threading.Thread):
	def __init__(self, name, args):
		threading.Thread.__init__(self)
		self.name = name
		self.stopreq = False
		self.done = False
		self.args = args
		self.msg = ""
		self.desc = "An innocent machine"
		self.is_ready = False

	def get_description(self):
		return self.desc
	
	def get_message(self):
		return self.msg
	
	def is_done(self):
		return self.done
	
	def stop(self):
		self.stopreq = True

	def process(self):
		pass

	def run(self):
		self.process()

class workermonitor(threading.Thread):
	results = []
	workers = []
	def __init__(self):
		threading.Thread.__init__(self)
		self.stop = False
		self.done = False

	@staticmethod
	def get_a_posibile_id(limit):
		if workermonitor.num_worker >= limit:
			return None
		wid = random.randint(11111, 99999)
		while workermonitor.get_worker(wid) is not None:
			wid = random.randint(11111, 99999)
		return wid

	@staticmethod
	def add_worker(wid, thr):
		workermonitor.workers.append({"name" : wid, "t" : thr})
		return wid

	@staticmethod
	def num_worker():
		return len(workermonitor.workers)
	
	@staticmethod
	def get_worker(wkname):
		for wk in workermonitor.workers:
			if wk['name'] == wkname:
				return wk['t']
		return None
	
	@staticmethod
	def get_result(wkname):
		for wk in workermonitor.results:
			if wk['name'] == wkname:
				return wk['r']
		return None
	
	def stopall(self):
		self.stop = True

	def safestop(self):
		while not self.done:
			time.sleep(1)

	def run(self):
		while not self.stop:
			for wk in self.workers:
				if wk["t"].is_done():
					workermonitor.results.append({"name" : wk["name"], "r" : wk["t"].get_message()})
					workermonitor.workers.remove({"name" : wk["name"], "t" : wk["t"]})
			time.sleep(10)

		print("Stoping other workers")
		for wk in self.workers:
			wk["t"].stop()
			while not wk["t"].is_done():
				time.sleep(0.1)
		self.done = True
		return 0