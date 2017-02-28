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


def member_names(class_to_check):
	''' Returns strings of a class' members '''
	return [getattr(class_to_check,member) for member in dir(class_to_check) 
		if '__' not in member]

if __name__ == '__main__': # List class members and assert key messages present

	# Outputs all class members
	for cls in [Uid,Req,Msg,Tcp]:
		print('['+repr(cls.__name__)+']')
		for member in member_names(cls): print(member)
		print('')

	# These should always be there
	assert 'marco' in member_names(Req)
	assert 'stop' in member_names(Req)
	assert 'polo' in member_names(Msg)
	assert 'started' in member_names(Msg)
	assert 'stopping' in member_names(Msg)

	Assert.success()