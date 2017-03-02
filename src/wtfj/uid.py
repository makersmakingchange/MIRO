''' Basically a constants file '''
''' Auth: max@embeddedprofessional.com '''

from wtfj_assert import *
import subprocess
import os

class Uid:
	''' List of the different components available at runtime '''
	GUI = 'gui'
	EYETRACKER = 'eyetracker'
	BLINK = 'blink'
	TEST = 'test'
	AUDIO = 'audio'
	CONSOLE = 'console'
	SYSTEM = 'system'
	PIECE = 'piece'


class Req:
	''' Message topics sent as requests to Pieces '''
	MARCO = 'marco'
	STOP = 'stop'
	SIZE = 'size'
	UPTIME = 'uptime'
	PERIOD = 'period'


class Msg:
	''' Message topics output from Pieces '''
	POLO = 'polo'
	STARTED = 'started'
	STOPPING = 'stopping'
	ERR = 'err'
	ACK = 'ack'
	USER = 'user'
	SELECT = 'select'
	IDLE = 'idle'


class Tcp:
	''' Networking constants '''
	SOCKET_SUB = 'tcp://localhost:5556'
	SOCKET_PUSH = 'tcp://localhost:5557'
	SOCKET_PUB = 'tcp://*:5556'
	SOCKET_PULL = 'tcp://*:5557'


def pack(uid,topic,data=None):
	''' Takes 2 or 3 arguments, the content of the third is unspecified '''
	assert uid in names(Uid)
	assert topic in names(Req) or topic in names(Msg)
	if data is None:
		return uid+' '+topic
	else:
		return uid+' '+topic+' '+bytes(data)

def unpack(msg):
	''' Returns a well-formed message or None '''
	msg_parts = msg.split(' ',2)
	n = len(msg_parts)
	if n == 3: return msg_parts
	if n == 2: return [msg_parts[0],msg_parts[1],None]
	return None

def name(piece):
	''' Returns id based on class name '''
	return piece.__class__.__name__.lower()

def names(class_to_check):
	''' Returns strings of a class' members '''
	return [getattr(class_to_check,member) for member in dir(class_to_check) 
		if '__' not in member]

def make_color(r_uint8,g_uint8,b_uint8):
	''' Color in 24-bit RGB format to '0x#######' string format '''
	r = '0x{:02x}'.format(r_uint8).replace('0x','')
	g = '0x{:02x}'.format(g_uint8).replace('0x','')
	b = '0x{:02x}'.format(b_uint8).replace('0x','')
	return '#'+r+g+b

def run_exe(uid):
	try:
		subprocess.Popen(['../bin/'+uid+'/'+ id+'.exe'])
	except OSError as e :
		pub.send_string('@err console '+ str(e))
		log_write('@err console '+ str(e))
	
def run_py_new_window(uid):
	try:
		subprocess.Popen(['python',uid+'.py'],
			creationflags=subprocess.CREATE_NEW_CONSOLE)
	except AttributeError as e: 
		pub.send_string('@err console '+ str(e))
		log_write('@err console '+ str(e))

def run_py(uid):
	subprocess.Popen(['python',uid+'.py'],
		shell=True,
		env=dict(os.environ))


if __name__ == '__main__': # List class members and assert key messages present

	# Outputs all class members
	for cls in [Uid,Req,Msg,Tcp]:
		print('['+repr(cls.__name__)+']')
		for member in names(cls): print(member)
		print('')

	# These names should always be there
	Assert(names(Req)).contains('marco')
	Assert(names(Req)).contains('stop')
	Assert(names(Msg)).contains('polo')
	Assert(names(Msg)).contains('started')
	Assert(names(Msg)).contains('stopping')