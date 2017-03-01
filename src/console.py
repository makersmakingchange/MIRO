'''
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
	function_dict['quit'](args)
	function_dict['start'](args)

def start_piece(args):
	if args[1] == 'all':
		pieces_to_start = all_pieces
	else:
		pieces_to_start = [args[1]]
	for piece in pieces_to_start:
		if piece == 'face' or piece == 'eyetracker':
			try:
				subprocess.Popen(['../bin/' + piece + '/' + piece + '.exe'])
			except OSError as e :
				pub.send_string('@err console '+ str(e))
				log_write('@err console '+ str(e))
		elif piece == 'output':
			try:
				subprocess.Popen(['python',piece+'.py'],
					creationflags=subprocess.CREATE_NEW_CONSOLE)
			except AttributeError as e: 
				pub.send_string('@err console '+ str(e))
				log_write('@err console '+ str(e))
		else:
			subprocess.Popen(['python',piece+'.py'],
				shell=True,
				env=dict(os.environ))

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

all_pieces = ['gui','audio','engine','face','output','blink','eyetracker']

function_dict = {}
function_dict['start'] = start_piece
function_dict['quit'] = quit_piece
function_dict['restart'] = restart_piece

alive = True
poll_thread = Thread(target=poll)
poll_thread.start()
'''
from wtfj import *

class Console(Piece):
	def _after_start(self):
		self._alert = False

	def _poll_event(self,data=None):
		if self._alert is True:
			print('hello')

	def _on_set(self,data=None):
		self._alert = data is 'alert'

class Armageddon(Piece):
	def _on_armageddon(self,data=None):
		import os
		while True:
			os.system("taskkill /im python.exe")

if __name__ == '__main__':
	import time

	zcc = ZmqClientConnector()
	armageddon = Armageddon(Uid.SYSTEM,zcc)

	zsc = ZmqServerConnector()
	console = Console(Uid.CONSOLE,zsc)

	#console.send('@system armageddon')

	user_in = None
	console.start()
	zcc.send('@console user What is wrong buddy?')
	try:
		while user_in != 'quit':
			user_in = raw_input('[$] ')
			console.send(user_in)
			print(zsc.poll())
	except EOFError:
		print('Console can not be read from, try running on command line')
	except KeyboardInterrupt as e:
		print(repr(e))
	
	console.stop()
	armageddon.stop()


'''
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
'''
		