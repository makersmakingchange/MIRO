import time
from threading import Thread
import threading
from uid import Uid,names

class Script:
	''' Runs a script passed as a list, default frequency = 1000Hz '''
	def __init__(self,msgs):
		self._msgs = msgs
		self._index = 0
		self._period = 0.001
		self._pid = 'SCRIPT'
	
	def send(self,string):
		''' Send TO this connector '''
		print(self._pid+' RECV < '+string)
		return self
	
	def poll(self,wait_s=None,uid=None):
		''' Poll FROM this connector '''
		period = self._period if wait_s is None else wait_s
		time.sleep(period)
		try:
			msg = self._msgs[self._index]
			print(self._pid+' SEND > '+msg)
			self._index += 1
			return [msg]
		except IndexError:
			return []

	def subscribe(self,*uids):
		for uid in uids:
			if uid is not None:
				if uid[0] is '@': assert uid[1:] in names(Uid)
				else: assert uid in names(Uid)
		return self

	def load(self,msg_array):
		self._msgs += msg_array
		return self

	def set_period(self,period):
		self._period = period
		return self

	def run(self):
		t = threading.current_thread()
		self._pid = str(t.ident)+' '+str(t.name)
		while len(self.poll()) > 0: pass

	def run_async(self):
		Thread(target=self.run).start()

if __name__ == '__main__':
	
	script = [
		'@other_uid topic data',
		'@other_uid topic',
		'uid topic data',
		'uid topic'
	]

	async = ['async topic '+str(n) for n in [1,2,3,4,5,6,7,8,9,0]]
	async2 = ['async2 topic '+str(n) for n in [1,2,3,4,5,6,7,8,9,0]]

	Script(script).set_period(1).run()
	Script(async).set_period(0.15).run_async()
	Script(async2).set_period(0.2).run_async()