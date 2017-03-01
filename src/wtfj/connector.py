import zmq
import time
from wtfj_assert import Assert
from uid import *


class Connector(object):
	''' Connects a client or server to i/o '''

	def send_string(self,string):
		raise NotImplementedError

	def recv_string(self,wait_s=1,uid=None):
		''' Must return a list of messages '''
		raise NotImplementedError

	def subscribe(self,uid):
		raise NotImplementedError


class ZmqClientConnector(Connector):
	''' Connects to tcp/ip on client side '''
	
	def __init__(self):
		context = zmq.Context()
		self._push = context.socket(zmq.PUSH)
		self._sub = context.socket(zmq.SUB)
		self._push.connect(Tcp.SOCKET_PUSH)
		self._sub.connect(Tcp.SOCKET_SUB)
		self._poller = zmq.Poller()
		self._poller.register(self._sub,zmq.POLLIN)

	def send(self,string):
		self._push.send_string(string)

	def poll(self,wait_s=1,uid=None):
		wait_ms = int(wait_s * 1000)
		events = self._poller.poll(timeout=wait_ms)
		return [self._sub.recv() for i in range(len(events))]

	def subscribe(self,uid):
		if isinstance(uid,bytes):
			uid = uid.decode('ascii')
		self._sub.setsockopt_string(zmq.SUBSCRIBE,uid)


class ZmqServerConnector(Connector):
	''' Bind to tcp/ip on server side '''

	def __init__(self):
		context = zmq.Context()
		self._pub = context.socket(zmq.PUB)
		self._pull = context.socket(zmq.PULL)
		self._pub.bind(Tcp.SOCKET_PUB)
		self._pull.bind(Tcp.SOCKET_PULL)
		self._poller = zmq.Poller()
		self._poller.register(self._pull,zmq.POLLIN)

	def send(self,string):
		self._pub.send_string(string)

	def poll(self,wait_s=1,uid=None):
		wait_ms = int(wait_s * 1000)
		events = self._poller.poll(timeout=wait_ms)
		return [self._pull.recv() for i in range(len(events))]

	def subscribe(self,uid):
		pass


class ScriptConnector(Connector):
	''' Runs a script passed as a list, default frequency = 1000Hz '''
	
	def __init__(self,msgs):
		self._msgs = msgs
		self._index = 0
		self._period = 0.001
	
	def send(self,string):
		''' Send TO this connector '''
		print('RECV < '+string)
		return self
	
	def poll(self,wait_s=None,uid=None):
		''' Poll FROM this connector '''
		period = self._period if wait_s is None else wait_s
		time.sleep(period)
		try:
			msg = self._msgs[self._index]
			print('SCRIPT > '+msg)
			self._index += 1
			return [msg]
		except IndexError:
			return []

	def subscribe(self,topic):
		return self

	def load(self,msg_array):
		self._msgs += msg_array
		return self

	def set_period(self,period):
		self._period = period
		return self

if __name__ == '__main__': # Unit test

	sc = ScriptConnector([
		'test marco',
		'test polo',
		'test get var'
	])
	
	start = time.clock()
	response = sc.poll()[0]
	Assert(response).equals(pack(Uid.TEST,Req.MARCO))

	response = sc.poll()[0]
	Assert(response).equals(pack(Uid.TEST,Msg.POLO))

	response = sc.poll()[0]
	Assert(response).equals(pack(Uid.TEST,Req.GET,'var'))
	delta = time.clock() - start
	Assert(delta < 0.1).equals(True)

	zcc = ZmqClientConnector()
	zcc2 = ZmqClientConnector()
	zcc3 = ZmqClientConnector()

	zsc = ZmqServerConnector()

	time.sleep(0.5)

	zcc.send('Hello')
	response = zsc.poll()[0]
	Assert(response).contains('Hello')

	zcc2.send('My')
	response = zsc.poll()[0]
	Assert(response).equals('My')

	zcc3.send('Baby')
	response = zsc.poll()[0]
	Assert(response).equals('Baby')