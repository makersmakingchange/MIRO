import time
from threading import Thread
from Queue import Queue,Empty
import traceback

try:
	DONTWAIT = zmq.DONTWAIT
except Exception:
	DONTWAIT = 1


class ClientPiece(object):
	def __init__(self,Uid):
		self._Uid = Uid
		self._ERR = 'err'
		self._STOP_MSG = 'stopping'
		self._START_MSG = 'started'
		self._alive = False
		self.flags = {}

	def start(self,subscriber,pusher,echo=False):
		self._birthday = time.clock()
		self._echo = echo
		self._interests = []
		self._sub = subscriber
		self._push = pusher
		self._alive = True
		poll_thread = Thread(target=self._poll)
		poll_thread.start()
		self._on_start()
		try:
			self._after_start()
		except AttributeError:
			pass

	def send(self,topic,data=''):
		''' Sends a message string to the server, whether a Python process or tcp '''
		self._push.send_string(self._Uid+' '+topic+' '+data)

	def send_to(self,Uid,topic,data=''):
		''' Constructs messages targeted for a specific client or service '''
		self._push.send_string('@'+Uid+' '+topic+' '+data)

	def err(self,msg):
		self.send(self._ERR,msg)

	def uptime(self):
		return time.clock() - self._birthday

	def add_interest(self,interest):
		self._interests.append(interest)

	def _poll(self):
		while self._alive == True:
			msg = self._sub.recv_string(DONTWAIT,self._Uid)
			if msg is not None:
				if self._interpret(msg) == False:
					if self._echo == True:
						self._push.send_string(msg)
			time.sleep(0.001)

	def _on_marco(self):
		self.send('polo',str(self.uptime()))

	def _on_stop(self,data=None):
		try:
			self._before_stop()
		except AttributeError:
			pass
		self._alive = False
		self.send(self._STOP_MSG)
		quit()

	def _on_start(self,data=None):
		self.send(self._START_MSG)

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
				if parts[0] == '@'+self._Uid:
					if size == 3:
						getattr(self,'_on_'+parts[1])(parts[2])
					else:
						getattr(self,'_on_'+parts[1])()
					ret = True
				elif parts[0] in self._interests:
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


class MyPiece(ClientPiece):
	def _on_foo(self,data=None):
		if data == None:
			self.send('foo')
		else:
			self.send('foo','with data '+data)

	def _after_start(self):
		self.size = None
		self.add_interest('gui')
		self.send_to('gui','get','size')
		self.send('_after_start','-this function called after successful start of piece')

	def _on_bar(self):
		self.send('BARDYBARBAR')

	def _before_stop(self):
		self.send('_before_stop','-this function called before attempting to stop piece')

	def _on_gui_size(self,data=None):
		#self.size = [int(x) for x in data.split[',',2][0:1]]
		self.send('ack','gui size')


class MockGuiPiece(ClientPiece):
	def _on_get(self,data=''):
		if data is not '':
			if data == 'size':
				self.send('size','1280,800')
				return
		self.err('get for variable ['+data+'] failed')


class ServerPiece(object):
	def __init__(self,echo=False):
		self._pull = Queue()
		self._pub = {}
		self._echo = echo

	def send_string(self,string):
		''' Sends a string to this server '''
		self._pull.put(string)
		try:
			Uid = string.split(' ',1)[0]
			self._pub[Uid].put(string)
		except KeyError:
			pass

	def recv_string(self,args=None,Uid=None):
		''' Returns a string in this server's buffer '''
		ret = None
		try:
			ret = self._pub['@'+Uid].get(block=(args != DONTWAIT))
		except Empty:
			pass
		except KeyError:
			pass
		return ret

	def publish(self,string):
		''' Puts message in outgoing queue '''
		Uid = string.split(' ',1)[0]
		try:
			found = self._pub[Uid]
		except KeyError:
			self._pub[Uid] = Queue()
		for key in self._pub:
			self._pub[key].put(string)	
		print('[sent] '+string)

	def pull(self,args=None):
		''' Returns messages in incoming queue '''
		ret = self._pull.get(block=(args != DONTWAIT))
		print('[recvd] '+ret)
		if self._echo == True:
			self.publish(ret)
		return ret

serv = ServerPiece(echo=True)

MockGuiPiece('gui').start(serv,serv)
serv.publish('@gui marco')
serv.pull()

MyPiece('max').start(serv,serv)
serv.pull()
serv.pull()
serv.pull()
serv.pull()
serv.pull()

start = time.clock()
serv.publish('@max marco')
serv.pull()
print('[delta '+str(time.clock() - start)+']')

serv.publish('@max stop')
serv.pull()
serv.pull()

serv.publish('@gui stop')
serv.pull()

MyPiece('max').start(serv,serv)
serv.publish('max laz ')
serv.pull()
serv.pull()
serv.pull()
serv.pull()

serv.publish('@max stop')
serv.pull()
serv.pull()