# For future compatibility with python 3
from __future__ import print_function
from __future__ import unicode_literals
# Python imports
import threading
import subprocess
# Third-party imports
import zmq

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
	in_parts = user_in.split()
	if in_parts[0] == 'start':
		subprocess.Popen(['python',in_parts[1]+'.py'])
	else:
		pub.send_string(user_in)
		if user_in == 'quit':
			alive = False
			quit()