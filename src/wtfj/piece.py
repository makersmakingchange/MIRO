import time
from threading import Thread
from Queue import Queue,Empty
import traceback

from wtfj_ids import *
from wtfj_utils import *
from wtfj_runner import *

class Piece(object):
	''' Pretty much everything in the system that's not a pipe is made of this '''
	''' Pieces are assigned identifiers based on their class '''
	def __init__(self,incoming,outgoing,uid=None,echo=False):
		''' Requires a unique identifier and incoming, outgoing supplying i/o '''
		''' Outgoing is set to incoming if None, uid is class name lowercase by default '''
		self._uid = get_uid(self)
		self._out = outgoing
		self._in = incoming
		self._echo = echo
		# Fail if connector does not have required functions
		try:
			assert 'send' in dir(self._out) 
		except AssertionError:
			print(get_uid(self._out)+' does not define send(self,uid,topic,data) function')
		try:
			assert 'poll' in dir(self._in)
		except AssertionError:
			print(get_uid(self._in)+' does not define poll(self,wait_ms=1,uid=None) function')
		try:
			assert 'subscribe' in dir(self._in)
		except AssertionError:
			print(get_uid(self._in)+' does not define subscribe(self,*uids) function')
		# Fail if uid not in list
		try:
			assert self._uid in get_attr(Uid)
		except AssertionError:
			print('['+self._uid+'] not in ['+str(get_attr(Uid))+']')
			raise AssertionError
		self._alive = False # Controls polling event loop
		self._period = 0.001 # Update period in seconds
		self._subscriptions = [] # List of uids to listen to besides own
		self._in.subscribe('@'+self._uid)

	def start(self):
		''' Starts the polling thread '''
		self._birthday = time.clock()
		# Set thread to live and start
		self._alive = True
		poll_thread = Thread(target=self._poll)
		try:
			self._BEFORE_start()
		except AttributeError:
			pass
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
		uid = ensure_delimited(uid)
		try:
			self._out.send(pack(uid,topic,data))
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
		try:
			if msg is not None:
				uid,topic,data = unpack(msg)
				# These are guaranteed to be in one of three states upon unpacking
				#
				# 	empty message 	: (None,None,None)
				# 	data is None	: (uid,topic,None)
				# 	full message 	: (uid,topic,None)
				#
				if uid[1:] == self._uid:
					try:
						getattr(self,'_ON_'+topic)(data)
						return True
					except AttributeError as e:
						self.err('No interpretation of message ['+msg+'] available')
						raise e
				elif uid in self._subscriptions:
					try:
						getattr(self,'_ON_'+uid+'_'+topic)(data)
						return True
					except AttributeError as e:
						#self.err('No interpretation of message ['+msg+'] available')
						#raise e
						pass # Fail silently if piece emits a signal
		except TypeError: return False
		except Exception as e:
			self.err('Exception thrown\n'+traceback.format_exc())
		return False
		
	def _poll(self):
		''' Run in its own thread '''
		while self._alive == True:
			# Loop through all new available messages
			msgs = self._in.poll(uid=self._uid,wait_s=self._period)
			for msg in msgs: 
				# Process each message
				if self._interpret(msg) == False:
					# Echo back out if can't consume it and _echo is set
					if self._echo == True: 
						self._out.send(msg)
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
		self.send(Msg.STOPPING)
		self._alive = False
		try:
			self._AFTER_stop()
		except AttributeError:
			pass

	def _ON_wait(self,data=None):
		time.sleep(float(data))

	def _ON_echo(self,data=None):
		if data is None:
			if self._echo == True:
				self.send(Req.ECHO,'on')
			else:
				self.send(Req.ECHO,'off')
		elif 'on' in data:
			self._echo = True 
			self.send(Msg.ACK)
		elif 'off' in data:
			self._echo = False
			self.send(Msg.ACK)

	def _ON_uptime(self,data=None):
		self.send(Req.UPTIME,str(time.clock() - self._birthday))

	def _ON_period(self,data=None):
		err_msg = 'Failed to set period, could not interpret ['+repr(data)+'] as float'
		try:
			self._period = float(data)
			return
		except ValueError as e:
			self.err(err_msg+'\n'+repr(e))
		except TypeError as e:
			self.err()

	@staticmethod
	def script(): 
		script = [
			'@piece marco',
			'@piece stop'
		]
		return Script(script)

if __name__ == '__main__': 
	from sys import argv
	Runner.run_w_cmd_args(Piece,argv)
