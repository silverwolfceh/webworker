import requests
import json
import threading
from data import country_all
import time


class smspool(threading.Thread):
	def __init__(self, srvid, key, name):
		threading.Thread.__init__(self)
		self.srvid = srvid
		self.apikey = key
		self.name = name
		self.min_price = 0
		self.min_country = ""
		self.success_rate = 100
		self.progress = 0
		self.stopreq = False
		self.done = False
		self.msg = ""

	def get_progress(self):
		return self.progress
	
	def get_message(self):
		return self.msg
	
	def is_done(self):
		return self.done
	
	def stop(self):
		self.stopreq = True

	def run(self):
		urltemplate = "https://api.smspool.net/request/price?country=%s&service=%s&key=%s&pool=&name=%s"
		totalcountries = len(country_all)
		pstep = int(totalcountries / 100)
		pcnt = 0
		for c in country_all:
			if self.stopreq:
				self.msg = "Forced stop"
				self.done = True
				return 1
			url = urltemplate  % (str(c["ID"]), self.srvid, self.apikey, c["name"])
			res = requests.get(url)
			if res.status_code == 200:
				data = res.json()
				print(data)
				try:
					if float(data["price"]) < self.min_price:
						self.min_price = float(data["price"])
						self.min_country = c["name"]
						self.success_rate = int(data["success_rate"])
					elif float(data["price"]) == self.min_price and int(data["success_rate"]) >= self.success_rate:
						self.min_price = float(data["price"])
						self.min_country = c["name"]
						self.success_rate = data["success_rate"]
					else:
						pass
				except:
					pass
			else:
				break
			pcnt = pcnt + 1
			self.progress = int((pcnt / 145)*100)
		if self.progress == 0:
			self.msg = "Something wrong"
			self.done = True
			return 1
		self.msg = "Srv: %s, Min-price: %s, Country: %s, Success rate: %s" % (self.srvid, self.min_price, self.min_country, self.success_rate)
		self.done = True
		return 0


class workermonitor(threading.Thread):
	results = []
	workers = []
	def __init__(self):
		threading.Thread.__init__(self)
		self.stop = False
		self.done = False

	@staticmethod
	def add_worker(name, thr):
		workermonitor.workers.append({"name" : name, "t" : thr})

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