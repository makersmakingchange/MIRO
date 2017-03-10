import time
from threading import Thread
import threading
from wtfj_ids import *
from wtfj_utils import *

class Printer:
	''' Opens a new output window and prints messages sent to it '''
	def __init__(self,header=''):
		self._header = header

	def send(self,string):
		print(self._header+string)

class Console:
	''' Allows user to enter commands '''
	def __init__(self,prompt='[$] '):
		self._prompt = prompt
		self._at = ''

	def poll(self,wait_s=None,uid=None):
		try:
			prompt = str(self._at)+str(self._prompt)
			msg = raw_input(prompt)
			if msg == '':
				self._at = ''
				return []
			if msg[0] == '@':
				self._at = msg.split()[0]+' '
			else:
				msg = self._at+msg
			return [msg]
		except Exception as e:
			print(repr(e))
			return []

	def subscribe(self,*uids):
		pass

class Script:
	''' Runs a script passed as a list, default frequency = 1000Hz '''
	def __init__(self,msgs):
		self._msgs = msgs
		self._index = 0
		self._period = 0.001
		self._pid = 'SCRIPT'
	
	def poll(self,wait_s=None,uid=None):
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
				if uid[0] is '@': assert uid[1:] in get_attr(Uid)
				else: assert uid in get_attr(Uid)
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
	
	Printer('A simple printer: ').send('Just printing a msg to current_thread')

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