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
log_name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.txt'
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

def start_piece(args):
	if args[1] == 'all':
		pieces_to_start = all_pieces
	else:
		pieces_to_start = [args[1]]
	for piece in pieces_to_start:
		if piece == 'face':
			subprocess.Popen(['../bin/face/face.exe'])
		elif piece == 'output':
			subprocess.Popen(['python',piece+'.py'],
				creationflags=subprocess.CREATE_NEW_CONSOLE)
		else:
			subprocess.Popen(['python',piece+'.py'])

def quit_piece(args):
	global alive
	if len(args) > 1:
		if args[1] == 'all':
			for piece in all_pieces:
				pub.send_string('@'+piece+' cmd=quit')
		else:
			pub.send_string('@'+args[1]+' cmd=quit')
	else:
		alive = False
		quit()

all_pieces = ['gui','audio','engine','face','output']

function_dict = {}
function_dict['start'] = start_piece
function_dict['quit'] = quit_piece

alive = True
poll_thread = threading.Thread(target=poll)
poll_thread.start()

while True:
	user_in = raw_input('[$] ')
	in_parts = user_in.split()
	try:
		function_dict[in_parts[0]](in_parts)
	except KeyError:
		pub.send_string(user_in)
	except IndexError:
		pass
	log_write(user_in)
		