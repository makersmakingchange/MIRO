import zmq
import time 


# Constants and stable vars
SOCKET_SUB = 'tcp://localhost:5556'
SOCKET_PUSH = 'tcp://localhost:5557'
BLINK_TIME = .15
topic_filter = '@blink'
interest_filter = 'eyetracker'
#interest_filter = 'mouse'
size_filter = 'gui'

# Connect to sockets
context = zmq.Context()
push = context.socket(zmq.PUSH)
sub = context.socket(zmq.SUB)
push.connect(SOCKET_PUSH)
sub.connect(SOCKET_SUB)
poller = zmq.Poller()
poller.register(sub,zmq.POLLIN)


# for python3 
if isinstance(topic_filter, bytes):
	topic_filter = topic_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,topic_filter)

# for python3 
if isinstance(interest_filter, bytes):
	interest_filter = interest_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,interest_filter)

# for python3 
if isinstance(size_filter, bytes):
	size_filter = size_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,size_filter)

def contain(pos,division,sel) :
	'''assume pos if a pair of coordinates'''
	x=int(pos[0])
	y=int(pos[1])
	selection = []
	division = division.split(',')
	contain =  False 
	for i in range(len(division)/4):
		if x > int(division[4*i]) and x < int(division[4*i+2]) and y >int(division[4*i+1]) and y<int(division[4*i+3]):
			sel = i
			print(sel)
			contain = True
	return contain
#send request to grab size of gui 
push.send_string('@gui regions=get')
division = ""
sel=0
msg = sub.recv_string().split()
if msg[1] == 'regions':
	regions = msg[2].split(",")
	division = ""
	for x in range(len(regions)):
		if (x%5 != 0):
			division = division + regions[x] + ","
	division = division[0:len(division)-1]

last_point = None 
last_time_unmatched = time.clock()
coor = ''

blink_detected = False

while True:    
	if len(poller.poll(1)) > 0:
		parts = sub.recv_string().split()
		# we got something
		if len(parts) > 0:
			try:

				if 'cmd=quit' in parts[1]:
					push.send_string('blink quitting')
					quit()
				coor = parts[2].split(',')
				if len(coor) > 0:
					last_time_unmatched = time.clock()
			except IndexError:
				push.send_string('@err blink not enough arguments')            
	else:
		try:
			#push.send_string('not receiving anything')
			if time.clock() - last_time_unmatched > BLINK_TIME:
				if blink_detected == False and contain(coor,division,sel):
					blink_detected = True
					push.send_string('@engine sel=' + str(sel))
			else:
				blink_detected = False
		except IndexError:
			pass		 
			
