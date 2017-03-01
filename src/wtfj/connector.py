from client_piece import *
from server_piece import *
import zmq

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
		self._msgs = [
			'@test marco',
			'@test marco',
			'@test stop'
			]
		self._index = 0
	
	def send(self,string):
		print('RECV < '+string)
	
	def poll(self,wait_ms=1,uid=None):
		time.sleep(wait_ms)
		try:
			msg = self._msgs[self._index]
			print('SCRIPT > '+msg)
			self._index += 1
			return [msg]
		except IndexError:
			return []

	def subscribe(self,topic):
		pass

if __name__ == '__main__': # Unit test

	zcc = ZmqClientConnector()
	zcc2 = ZmqClientConnector()
	zcc3 = ZmqClientConnector()

	zsc = ZmqServerConnector()

	time.sleep(0.5)

	zcc.send('Hello')
	zcc2.send('My')
	zcc3.send('Baby')

	response = zsc.poll()
	Assert(response).contains('Hello')

	response2 = zsc.poll()
	Assert(response2).equals('My')
	
	response3 = zsc.poll()
	Assert(response3).equals('Baby')

	cp = ClientPiece(Uid.TEST)
	cp.stop()