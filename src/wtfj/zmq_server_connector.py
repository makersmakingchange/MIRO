import zmq
from uid import Tcp
from connector import Connector

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
		return False