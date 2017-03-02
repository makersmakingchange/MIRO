import time
from threading import Thread
from Queue import Queue,Empty
import traceback

from wtfj_ids import *
from wtfj_utils import *
from connectors_local import *


class Piece(object):
	''' Pretty much everything in the system that's not a pipe is made of this '''
	''' Pieces are assigned identifiers based on their class '''
	def __init__(self,incoming,outgoing=None,uid=None):
		''' Requires a unique identifier and incoming, outgoing supplying i/o '''
		''' Outgoing is set to incoming if None, uid is class name lowercase by default '''
		self._uid = name(self) if uid is None else uid
		self._out = incoming if outgoing is None else outgoing
		self._in = incoming
		# Fail if connector does not have required functions
		assert 'send' in dir(self._out) 
		assert 'poll' in dir(self._in)
		assert 'subscribe' in dir(self._in)
		# Fail if uid not in list
		try:
			assert self._uid in names(Uid)
		except AssertionError:
			print('['+self._uid+'] not in ['+str(names(Uid))+']')
			raise AssertionError
		self._alive = False # Controls polling event loop
		self._period = 0.001 # Update period in seconds
		self._subscriptions = [] # List of uids to listen to besides own
		self._in.subscribe('@'+self._uid)

	def start(self,echo=False):
		''' Starts the polling thread '''
		self._birthday = time.clock()
		self._echo = echo
		# Set thread to live and start
		self._alive = True
		poll_thread = Thread(target=self._poll)
		poll_thread.start()
		self.send(Msg.STARTED)
		try:
			self._AFTER_start()
		except AttributeError:
			pass
		return self

	def stop(self):
		''' Public access to stop the polling loop '''
		self._ON_stop()

	def send(self,topic,data=None):
		''' Sends a message string to the connector '''
		try:
			self._out.send(pack(self._uid,topic,data))
		except AssertionError as e:
			self.err('Uid or topic invalid for msg ['+str(topic)+']['+str(data)+']\n'+repr(e))

	def send_to(self,uid,topic,data=''):
		''' Sends a message string targeted for a specific client or service '''
		''' The connector bears responsibility for proper routing '''
		try:
			self._out.send(pack('@'+uid,topic,data))
		except AssertionError as e:
			self.err('Uid or topic invalid for msg ['+str(topic)+']['+str(data)+']\n'+repr(e))
		return self

	def subscribe(self,*uids):
		''' Keep a list of subscriptions and set in connector'''
		self._in.subscribe(*uids)
		for uid in uids:
			self._subscriptions.append(uid)
		return self

	def err(self,msg):
		self.send(Msg.ERR,msg)
		return self

	def _interpret(self,msg):
		''' Attempts to parse the incoming packet '''
		''' Calls a function based on the msg content '''
		parts = unpack(msg)
		if parts is None: 
			self.err('Malformed message ['+msg+'], found '+str(len(parts))+' of minimum 2 arguments')
			return False
		uid,topic,data = parts # Data may equal None
		try:
			if uid == '@'+self._uid:
				try:
					getattr(self,'_ON_'+topic)(data)
				except AttributeError as e:
					self.err('No interpretation of message ['+msg+'] available')
					return False
			elif uid in self._subscriptions:
				try:
					getattr(self,'_ON_'+uid+'_'+topic)(data)
				except AttributeError:
					return False
		except Exception as e:
			self.err('Exception thrown\n'+traceback.format_exc())
			return False
		return True

	def _poll(self):
		''' Run in its own thread '''
		while self._alive == True:
			# Loop through all new available messages
			msgs = self._in.poll(uid=self._uid,wait_s=self._period)
			for msg in msgs: 
				# Process each message
				if self._interpret(msg) == False:
					# Echo back out if can't consume it and _echo is set
					if self._echo == True: self._conn.send(msg)
			try:
				self._DURING_poll()
			except AttributeError:
				pass

	def _ON_marco(self,data=None):
		self.send(Msg.POLO)

	def _ON_stop(self,data=None):
		try:
			self._BEFORE_stop()
		except AttributeError:
			pass
		self._alive = False
		self.send(Msg.STOPPING)

	def _ON_uptime(self,data=None):
		self.send(Req.UPTIME,str(time.clock() - self._birthday))

	def _ON_period(self,data=None):
		try:
			self._period = float(data)
			return
		except ValueError:
			pass
		except TypeError:
			pass
		self.err('Failed to set period, could not interpret ['+repr(data)+'] as float')


if __name__ == '__main__': # Make a test server, start client, quit
	
	script = [
		'@piece marco',
		'@piece period 1',
		'@piece uptime',
		'@piece uptime',
		'@piece period 0.1',
		'@piece uptime',
		'@piece uptime',
		'@piece throw error',
		'@piece stop'
	]

	Piece(Script(script),Printer('RECV < ')).start()
