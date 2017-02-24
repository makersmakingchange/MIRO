# For future compatibility with python 3
from __future__ import print_function
from __future__ import unicode_literals
# Python imports
import threading
import subprocess
import time
import datetime
# Third-party imports
import zmq

# Start clock
time.clock()

# Constants
SOCKET_PUB = 'tcp://*:5556'
SOCKET_PULL = 'tcp://*:5557'
LOG_PATH = '../log/'

# Create sockets and poller
context = zmq.Context()
pub = context.socket(zmq.PUB)
pull = context.socket(zmq.PULL)
pub.bind(SOCKET_PUB)
pull.bind(SOCKET_PULL)
poller = zmq.Poller()
poller.register(pull,zmq.POLLIN)

# Open log file for appending
log_name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.log'
log = open(LOG_PATH+log_name,'w+')
log_lock = threading.Lock()

def log_write(msg):
	log_lock.acquire()
	log_msg = str(time.clock())+' '+msg+'\n'
	log.write(log_msg)
	log_lock.release()

def poll():
	while alive:
		events = poller.poll(1)
		if len(events) > 0:
			msg = pull.recv()
			pub.send_string(msg)
			log_write(msg)

alive = True
poll_thread = threading.Thread(target=poll)
poll_thread.start()

available_modules = ['gui','audio','engine']

while True:
	user_in = raw_input('[$] ')
	in_parts = user_in.split()
	if len(in_parts) > 0:
		if in_parts[0] == 'start':
			if len(in_parts) > 1:
				if in_parts[1] == 'all':
					for available_module in available_modules:
						subprocess.Popen(['python',available_module+'.py'])
				else:
					subprocess.Popen(['python',in_parts[1]+'.py'])
		elif in_parts[0] == 'quit':
			if len(in_parts) > 1:
				if in_parts[1] == 'all':
					for available_module in available_modules:
						pub.send_string('@'+available_module+' cmd=quit')
			alive = False
			log.close()
			quit()
		else:
			pub.send_string(user_in)
		log_write(user_in)