# See wtfj/__init__.py for full list of imports
from wtfj import *
import subprocess
import os
import time
import datetime

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
log_lock = Lock()

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

def restart_piece(args):
	function_dict['stop'](args)
	function_dict['start'](args)

def start_piece(args):
	try:
		Runner.run(args[1],args[2])
	except IndexError:
		print('Bad args '+str(args)+' should be in form ["start piece mode"] e.g. start tkpiece test')

def stop_piece(args):
	global alive
	if len(args) > 1:
		if args[1] == 'all':
			for piece in all_pieces:
				pub.send_string('@'+piece+' stop')
		else:
			pub.send_string('@'+args[1]+' stop')
	else:
		alive = False
		quit()

function_dict = {}
function_dict['start'] = start_piece
function_dict['stop'] = stop_piece
function_dict['restart'] = restart_piece

alive = True
poll_thread = Thread(target=poll)
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
		