''' Basically a constants file '''
''' Auth: max@embeddedprofessional.com '''

def name(piece):
	''' Returns id based on class name '''
	return piece.__class__.__name__.lower()

def names(class_to_check):
	''' Returns strings of a class' members '''
	return [getattr(class_to_check,member) for member in dir(class_to_check) 
		if '__' not in member]

class Uid:
	''' List of the different components available at runtime '''
	GUI = 'gui'
	EYETRACKER = 'eyetracker'
	BLINK = 'blink'
	TEST = 'test'
	AUDIO = 'BLARg'
	CONSOLE = 'console'
	SYSTEM = 'system'
	TKPIECE = 'tkpiece'
	PIECE = 'piece'


class Mode:
	''' List of different operating conditions '''
	CONSOLE = 1 << 0
	TEST = 1 << 1
	EXE = 1 << 2
	ZMQ = 1 << 3


class Req:
	''' Message topics sent as requests to Pieces '''
	MARCO = 'marco'
	STOP = 'stop'
	SIZE = 'size'
	UPTIME = 'uptime'
	PERIOD = 'period'
	FONT = 'font'


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
	MOUSE = 'mouse'
	CONSOLE = 'console'
	MODE = 'mode'


class Tcp:
	''' Networking constants '''
	SOCKET_SUB = 'tcp://localhost:5556'
	SOCKET_PUSH = 'tcp://localhost:5557'
	SOCKET_PUB = 'tcp://*:5556'
	SOCKET_PULL = 'tcp://*:5557'


if __name__ == '__main__': # List class members and assert key messages present

	# Outputs all class members
	for cls in [Uid,Mode,Req,Msg,Tcp]:
		print('['+repr(cls.__name__)+']')
		for member in names(cls): print(member)
		print('')

	# These names should always be there
	assert 'marco' in names(Req)
	assert 'polo' in names(Msg)
	assert 'started' in names(Msg)
	assert 'stopping' in names(Msg)