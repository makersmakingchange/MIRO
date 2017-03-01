''' Basically a constants file '''
''' Auth: max@embeddedprofessional.com '''

from wtfj_assert import *


class Uid:
	''' List of the different components available at runtime '''
	GUI = 'gui'
	EYETRACKER = 'eyetracker'
	BLINK = 'blink'
	TEST = 'test'


class Req:
	''' Message topics sent as requests to Pieces '''
	MARCO = 'marco'
	STOP = 'stop'
	GET = 'get'


class Msg:
	''' Message topics output from Pieces '''
	POLO = 'polo'
	STARTED = 'started'
	STOPPING = 'stopping'
	ERR = 'err'
	SIZE = 'size'
	ACK = 'ack'
	UPTIME = 'uptime'


class Tcp:
	''' Networking constants '''
	SOCKET_SUB = 'tcp://localhost:5556'
	SOCKET_PUSH = 'tcp://localhost:5557'
	SOCKET_PUB = 'tcp://*:5556'
	SOCKET_PULL = 'tcp://*:5557'


def pack(uid,topic,data=None):
	if data is None:
		return uid+' '+topic
	else:
		return uid+' '+topic+' '+str(data)

def unpack(msg):
	msg_parts = msg.split(' ',2)
	n = len(msg_parts)
	if n == 3: return msg_parts
	if n == 2: return [msg_parts[0],msg_parts[1],None]
	return None

def names(class_to_check):
	''' Returns strings of a class' members '''
	return [getattr(class_to_check,member) for member in dir(class_to_check) 
		if '__' not in member]


if __name__ == '__main__': # List class members and assert key messages present

	# Outputs all class members
	for cls in [Uid,Req,Msg,Tcp]:
		print('['+repr(cls.__name__)+']')
		for member in names(cls): print(member)
		print('')

	# These should always be there
	Assert(names(Req)).contains('marco')
	Assert(names(Req)).contains('stop')
	Assert(names(Msg)).contains('polo')
	Assert(names(Msg)).contains('started')
	Assert(names(Msg)).contains('stopping')