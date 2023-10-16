import sys
sys.path.append('../')
from worker import webworker

class spamotp(webworker):
    def __init__(self, name, args = {}):
        super().__init__(name, args)
        self.desc = "Spam OTP to a phone number"

    def process(self):
        pass