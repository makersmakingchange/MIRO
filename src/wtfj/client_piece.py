import time
from threading import Thread
from Queue import Queue,Empty
import traceback

from uid import *
from connector import *


class ClientPiece(object):
	def __init__(self,uid,connector):
		''' Requires a unique identifier and a connector supplying i/o '''
		assert uid in names(Uid) # Fail if unique id not in master list
		self._uid = uid
		# Fail if connector does not have required functions
		members = dir(connector)
		assert 'send' in members
		assert 'poll' in members
		assert 'subscribe' in members
		self._conn = connector
		self._alive = False # Controls polling event loop
		self._period = 0.001 # Update period in seconds
		self._subscriptions = [] # List of uids to listen to besides own

	def start(self,echo=False):
		''' Starts the polling thread '''
		self._birthday = time.clock()
		self._echo = echo
		self.subscribe('@'+self._uid)
		# Set thread to live and start
		self._alive = True
		poll_thread = Thread(target=self._poll)
		poll_thread.start()
		self._on_start()
		try:
			self._after_start()
		except AttributeError:
			pass

	def stop(self):
		''' Public access to stop the polling loop '''
		self._on_stop()

	def send(self,topic,data=None):
		''' Sends a message string to the server, whether a Python process or tcp '''
		msg = pack(self._uid,topic,data)
		########### INTERFACE ##########
		self._conn.send(msg)
		############ OUTPUT ############

	def send_to(self,uid,topic,data=''):
		''' Constructs messages targeted for a specific client or service '''
		msg = pack('@'+uid,topic,data)
		########### INTERFACE ##########
		self._conn.send(msg)
		############ OUTPUT ############

	def subscribe(self,topic):
		''' Keep a list of subscriptions and set in connector'''
		self._conn.subscribe(topic)
		self._subscriptions.append(topic)

	def err(self,msg):
		self.send(Msg.ERR,msg)

	def _on_uptime(self,data=None):
		self.send(Msg.UPTIME,str(time.clock() - self._birthday))

	def _poll(self):
		''' Run in its own thread '''
		while self._alive == True:
			while True:
				msg = self._conn.poll(uid=self._uid) # GET ONE INCOMING MESSAGE
				if msg is None: break
				if self._interpret(msg) == False:
					if self._echo == True: self._conn.send(msg) # ECHO OUT
			time.sleep(self._period)
			try:
				self._poll_event()
			except AttributeError:
				pass

	def _on_marco(self,data=None):
		self.send(Msg.POLO)

	def _on_stop(self,data=None):
		try:
			self._before_stop()
		except AttributeError:
			pass
		self._alive = False
		self.send(Msg.STOPPING)

	def _on_start(self,data=None):
		self.send(Msg.STARTED)

	def _interpret(self,msg):
		''' 
		Attempts to parse the incoming packet 
		Calls a function based on the msg content
		'''
		parts = unpack(msg)
		if parts is None: 
			self.err('malformed message ['+msg+'], found '+str(len(parts))+' of minimum 2 arguments')
			return False

		uid,topic,data = parts # Data may equal None

		try:
			if uid == '@'+self._uid:
				try:
					getattr(self,'_on_'+topic)(data)
				except AttributeError as e:
					self.err('no interpretation of message ['+msg+'] available')
					return False
			elif uid in self._subscriptions:
				try:
					getattr(self,'_on_'+uid+'_'+topic)(data)
				except AttributeError:
					return False
		except Exception as e:
			self.err('exception thrown\n'+traceback.format_exc())
			return False
		return True

if __name__ == '__main__': # Make a test server, start client, quit
	
	sc = ScriptConnector()
	sc.set_frequency(10)
	sc.set_msgs([
		'First polling event',
		pack('@'+Uid.TEST,Req.MARCO),
		pack('@'+Uid.TEST,Req.MARCO),
		pack('@'+Uid.TEST,Req.STOP)
		])
	sc.poll()

	cp = ClientPiece(Uid.TEST,sc)
	cp.start()
	time.sleep(1)

