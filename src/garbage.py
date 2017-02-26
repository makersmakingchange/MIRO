import zmq
import time 


# Constants and stable vars
SOCKET_SUB = 'tcp://localhost:5556'
SOCKET_PUSH = 'tcp://localhost:5557'
topic_filter = 'eyetracker'

# Connect to sockets
context = zmq.Context()
push = context.socket(zmq.PUSH)
sub = context.socket(zmq.SUB)
push.connect(SOCKET_PUSH)
sub.connect(SOCKET_SUB)



# for python3 
if isinstance(topic_filter, bytes):
    topic_filter = topic_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,topic_filter)



        
last_point = None 
last_time_unmatched = time.clock()
coor = ''
x = 0
y = 0
size = (1080,720)
while True:  
    try:
            message = sub.recv_string(zmq.DONTWAIT)
            parts = message.split()
            # we got something 
            if len(parts) > 0:
                

                coor = parts[1]
                coor = coor.split(',')
                if len(coor) > 0:
                    # do the checking 
                    if (last_point != None):
                        if coor[0] == last_point[0] and coor[1] == last_point[1]:
                            if time.clock() - last_time_unmatched > 2 :
                                if int(x) < 0.5*size[0]:
                                    push.send_string('@engine sel=0')
                                else :
                                    push.send_string('@engine sel=1')
                        else :
                                last_time_unmatched = time.clock()
                    if 'cmd=quit' in message:
    	                quit()
                    last_point = coor
                    x = coor[0]
                    y = coor[1]

    except zmq.Again:
            #push.send_string('not receiving anything')
            if time.clock() - last_time_unmatched >5 :
                
                push.send_string('last x coordinate is '+ str(x))
                if float(x) < 0.5*size[0]:
                    push.send_string('@engine sel=0')
                else :
                    push.send_string('@engine sel=1')
                last_time_unmatched = time.clock()
                                 
            
