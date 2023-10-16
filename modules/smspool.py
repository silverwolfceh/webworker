import sys
sys.path.append('../')
from worker import webworker
import requests
import json
from .smspooldata import country_all
import time


class smspool(webworker):
	def __init__(self, name, args):
		super().__init__(name, args)
		self.name = name
		self.min_price = 99
		self.min_country = ""
		self.success_rate = 100
		self.progress = 0
		self.stopreq = False
		self.done = False
		self.msg = ""
		self.desc = "To find the cheapest price for a service id"
		self.init_params(args)


	def init_params(self, args):
		try:
			self.srvid = args.get('srvid', '')
			self.apikey = args.get('key', 'VFoCdZK4WjDeArKacB43cE1K0Intx2Vu')
		except:
			print("Not valid argument", self.name)
			return

	def get_progress(self):
		return self.progress
	
	def get_message(self):
		return self.msg
	
	def is_done(self):
		return self.done
	
	def stop(self):
		self.stopreq = True

	def process(self):
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
		self.msg = "Srv: %s, Min-price: %s, Country: %s, Success rate: %s" % (self.srvid, str(self.min_price), self.min_country, self.success_rate)
		self.done = True
		return 0