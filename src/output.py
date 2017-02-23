# For future compatibility with python 3
from __future__ import print_function
from __future__ import unicode_literals
# Third-party imports
import zmq

# Constants and stable vars
SOCKET_SUB = 'tcp://localhost:5556'
topic_filter = ''

# Connect to sockets
context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect(SOCKET_SUB)

if isinstance(topic_filter,bytes):
	topic_filter = topic_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,topic_filter)

while True:
	string = sub.recv_string()
	parts = string.split()
	if len(parts) > 1:
		if parts[0] == 'output' and parts[1] == 'cmd=quit':
			quit()
	print(string)
