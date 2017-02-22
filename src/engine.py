import zmq

# Constants and stable vars
SOCKET_SUB = 'tcp://localhost:5556'
SOCKET_PUSH = 'tcp://localhost:5557'
topic_filter = 'engine'
topic_audio = 'audio'

# Connect to sockets
context = zmq.Context()
push = context.socket(zmq.PUSH)
sub = context.socket(zmq.SUB)
push.connect(SOCKET_PUSH)
sub.connect(SOCKET_SUB)

if isinstance(topic_filter,bytes):
	topic_filter = topic_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,topic_filter)

options = [
	'a',
	'b',
	'c',
	'<'
]

def command(cmd_string):
	if cmd_string == 'quit':
		quit()

def select(sel_string):
	try:
		option_sel = options[int(sel_string)]
		option_msg = topic_audio+' '+option_sel
		push.send_string(option_msg)
	except IndexError:
		pass
	except ValueError:
		pass

def option(opt_string):
	pass

function_dict = {}
function_dict['cmd'] = command
function_dict['sel'] = select
function_dict['opt'] = option

while True:
	string = sub.recv_string()
	parts = string.split()
	if len(parts) > 0:
		msg_parts = parts[1].split('=')
		if len(msg_parts) > 0:
			try:
				function_dict[msg_parts[0]](msg_parts[1])
			except KeyError:
				pass





