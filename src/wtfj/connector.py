import zmq
import time
from wtfj_assert import Assert
from uid import *


class Connector(object):
	''' Connects a client or server to i/o '''

	def send_string(self,string):
		raise NotImplementedError

	def recv_string(self,wait_ms=1,uid=None):
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

	def poll(self,wait_ms=1,uid=None):
		events = self._poller.poll(timeout=wait_ms)
		if len(events) > 0:
			return self._sub.recv()
		return None

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

	def poll(self,wait_ms=1,uid=None):
		events = self._poller.poll(timeout=wait_ms)
		if len(events) > 0:
			return self._pull.recv()
		return None

	def subscribe(self,uid):
		pass


class ScriptConnector(object):
	def __init__(self):
		self._msgs = []
		self._index = 0
		self._period = 0.001
	
	def send(self,string):
		''' Send TO this connector '''
		print('RECV < '+string)
	
	def poll(self,wait_ms=None,uid=None):
		''' Poll FROM this connector '''
		time.sleep(self._period)
		try:
			msg = self._msgs[self._index]
			print('SCRIPT > '+msg)
			self._index += 1
			return msg
		except IndexError:
			return None

	def subscribe(self,topic):
		pass

	def set_frequency(self,f_Hz):
		self._period = 1.0/float(f_Hz);

	def set_msgs(self,msg_array):
		self._msgs = msg_array

if __name__ == '__main__': # Unit test

	sc = ScriptConnector()
	sc.set_frequency(3.333)
	sc.set_msgs([
		pack(Uid.TEST,Req.MARCO),
		pack(Uid.TEST,Msg.POLO),
		pack(Uid.TEST,Req.GET,'var')
		])
	
	start = time.clock()
	Assert(sc.poll()).equals('test marco')
	Assert(sc.poll()).equals('test polo')
	Assert(sc.poll()).equals('test get var')
	delta = time.clock() - start
	Assert(delta > 0.9 and delta < 1.11).equals(True)

	zcc = ZmqClientConnector()
	zcc2 = ZmqClientConnector()
	zcc3 = ZmqClientConnector()

	zsc = ZmqServerConnector()

	time.sleep(0.5)

	zcc.send('Hello')
	time.sleep(0.5)
	zcc2.send('My')
	time.sleep(0.5)
	zcc3.send('Baby')

	response = zsc.poll()
	Assert(response).contains('Hello')

	response2 = zsc.poll()
	Assert(response2).equals('My')
	
	response3 = zsc.poll()
	Assert(response3).equals('Baby')