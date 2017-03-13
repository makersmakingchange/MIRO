import zmq
from wtfj_ids import *
from wtfj_utils import *

class ZmqPublisher:
	''' Publisher that acts as server output '''
	def __init__(self):
		context = zmq.Context()
		self._pub = context.socket(zmq.PUB)
		self._pub.bind(Tcp.SOCKET_PUB)

	def send(self,string):
		self._pub.send_string(string)


class ZmqSubscriber:
	''' Client receiver for publisher above '''
	''' Subcription should really take place in the Piece this connects to '''
	def __init__(self,*uids):
		context = zmq.Context()
		self._sub = context.socket(zmq.SUB)
		self._sub.connect(Tcp.SOCKET_SUB)
		self._poller = zmq.Poller()
		self._poller.register(self._sub,zmq.POLLIN)
		self.subscribe(*uids)

	def poll(self,wait_s=1,uid=None):
		wait_ms = int(wait_s * 1000)
		events = self._poller.poll(timeout=wait_ms)
		return [self._sub.recv() for i in range(len(events))]

	def subscribe(self,*uids):
		for uid in uids:
			if uid is not None:
				if uid[0] is '@': 
					assert uid[1:] in get_attr(Uid)
				else: assert uid in get_attr(Uid)
				if isinstance(uid,bytes):
					uid = ''
					uid = uid.decode('ascii')
				try:
					self._sub.setsockopt_string(zmq.SUBSCRIBE,uid)
					return True
				except Exception as e:
					print(e)
					return False
		return self


class ZmqPusher:
	''' Pushes client msgs back to server '''
	def __init__(self):
		context = zmq.Context()
		self._push = context.socket(zmq.PUSH)
		self._push.connect(Tcp.SOCKET_PUSH)

	def send(self,string):
		self._push.send_string(string)


class ZmqPuller:
	''' Pulls messages into server '''
	def __init__(self):
		context = zmq.Context()
		self._pull = context.socket(zmq.PULL)
		self._pull.bind(Tcp.SOCKET_PULL)
		self._poller = zmq.Poller()
		self._poller.register(self._pull,zmq.POLLIN)

	def poll(self,wait_s=1,uid=None):
		wait_ms = int(wait_s * 1000)
		events = self._poller.poll(timeout=wait_ms)
		return [self._pull.recv() for i in range(len(events))]

	def subscribe(self,*uids):
		for uid in uids:
			if uid is not None:
				if uid[0] is '@': assert uid[1:] in get_attr(Uid)
				else: assert uid in get_attr(Uid)
		return self


if __name__ == '__main__': # Set up client and server connections and test

	import time
	print('Send a test message from client to server and server to client')

	# Server connections
	zpub = ZmqPublisher() # Publishes messages to all subscribers
	zpull = ZmqPuller() # Pulls messages fom all subscribers

	# Client connections
	zsub = ZmqSubscriber('@test') # Filters incoming messages to uid 'test'
	zpush = ZmqPusher() # Pushes messages back to server

	time.sleep(1)
	zpub.send('@test marco')
	time.sleep(1)
	assert zsub.poll() == ['@test marco']

	start = time.clock()

	zpush.send('test polo')
	time.sleep(1)
	assert zpull.poll() == ['test polo']
	delta = time.clock() - start

	print('Success')
	print('Timing error of %.2f %%' % float(100*(delta-1)))