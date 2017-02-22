# Test server for sound component
# binds PUB socket to tcp://*:5556

import zmq
import threading

# Constants
SOCKET_PUB = 'tcp://*:5556'
SOCKET_PULL = 'tcp://*:5557'

# Create sockets and poller
context = zmq.Context()
pub = context.socket(zmq.PUB)
pull = context.socket(zmq.PULL)
pub.bind(SOCKET_PUB)
pull.bind(SOCKET_PULL)
poller = zmq.Poller()
poller.register(pull,zmq.POLLIN)

def poll():
	global alive
	while alive:
		events = poller.poll(1)
		if len(events) > 0:
			message = pull.recv()
			pub.send_string(message)

alive = True
poll_thread = threading.Thread(target=poll)
poll_thread.start()

while True:
	user_in = raw_input('[$] ')
	pub.send_string(user_in)
	if user_in == 'quit':
		alive = False
		quit()