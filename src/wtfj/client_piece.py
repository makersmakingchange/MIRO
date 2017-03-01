import time
from threading import Thread
from Queue import Queue,Empty
import traceback

from uid import *

try:
	DONTWAIT = zmq.DONTWAIT
except Exception:
	DONTWAIT = 1

class ClientPiece(object):
	def __init__(self,uid):
		self._uid = uid
		self._alive = False
		self.flags = {}
		self._subscriptions = []
		assert self._uid in member_names(Uid)

	def start(self,connector,echo=False):
		self._birthday = time.clock()
		self._echo = echo
		self._connector = connector
		self._alive = True
		self.subscribe('@'+self._uid)
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

	def send(self,topic,data=''):
		''' Sends a message string to the server, whether a Python process or tcp '''
		if data == '':
			msg = self._uid+' '+topic
		else:
			msg = self._uid+' '+topic+' '+data
		########### INTERFACE ##########
		self._connector.send_string(msg)
		############ OUTPUT ############

	def send_to(self,uid,topic,data=''):
		''' Constructs messages targeted for a specific client or service '''
		if data == '':
			msg = '@'+uid+' '+topic
		else:
			msg = '@'+uid+' '+topic+' '+data
		########### INTERFACE ##########
		self._connector.send_string(msg)
		############ OUTPUT ############

	def err(self,msg):
		self.send(Msg.ERR,msg)

	def _on_uptime(self):
		self.send(Msg.UPTIME,str(time.clock() - self._birthday))

	def subscribe(self,topic):
		''' Keep a list of subscriptions and set in connector'''
		self._connector.subscribe(topic)
		self._subscriptions.append(topic)

	def _poll(self,period_s=0.001):
		''' Run in its own thread '''
		''' This is the only network for this Piece '''
		while self._alive == True:
			################## INTERFACE ###################
			msg = self._connector.recv_string(uid=self._uid)
			#################### INPUT #####################
			if msg is not None:
				if self._interpret(msg) == False:
					if self._echo == True:
						########### INTERFACE ##########
						self._connector.send_string(msg)
						############ OUTPUT ############
			time.sleep(0.1)
		try:
			self._poll_event()
		except AttributeError:
			pass

	def _on_marco(self):
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
		self._last_msg_time = time.clock()
		ret = False
		fail_silent = False
		parts = msg.split(' ',2)
		try:
			size = len(parts)
			if size < 2:
				self.err('malformed message ['+msg+'], found '+str(size)+' of minimum 2 arguments')
			else:
				if parts[0] == '@'+self._uid:
					if size == 3:
						getattr(self,'_on_'+parts[1])(parts[2])
					else:
						getattr(self,'_on_'+parts[1])()
					ret = True
				elif parts[0] in self._subscriptions:
					# Fail silently when receiving a message from an interest as most of these
					# will not be mapped to functions to handle them
					fail_silent = True
					if size == 3:
						getattr(self,'_on_'+parts[0]+'_'+parts[1])(parts[2])
					else:
						getattr(self,'_on_'+parts[0]+'_'+parts[1])()
					ret = True
		except AttributeError as e:
			if not fail_silent: self.err('no interpretation of message ['+msg+'] available')
		except Exception as e:
			self.err('exception thrown\n'+traceback.format_exc())
		return ret

if __name__ == '__main__': # Make a test server, start client, quit
	
	from server_piece import *
	serv = ServerPiece(echo=True)
	
	cp = ClientPiece(Uid.TEST)
	cp.start(serv)
	serv.poll()

	serv.send_to(Uid.TEST,Req.MARCO)
	Assert(serv.poll(1)).sent_by(Uid.TEST).topic_is(Msg.POLO)
	
	time.sleep(1)

	cp.stop()

	serv.poll()

