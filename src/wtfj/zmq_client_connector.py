import zmq
from uid import Tcp
from connector import Connector


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
		try:
			self._sub.setsockopt_string(zmq.SUBSCRIBE,uid)
			return True
		except zmq.err.ZMQError as e:
			print(e)
			return False


if __name__ == '__main__': # Doesn't really do much by itself
	import time

	zcc = ZmqClientConnector()
	
	start = time.clock()
	assert len(zcc.poll(1)) == 0 # Received no messages
	delta = time.clock() - start
	print('Timing error of %.2f %%' % float(100*(delta-1)))