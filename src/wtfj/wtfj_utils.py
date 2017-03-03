from wtfj_ids import Uid,Req,Msg,Mode,name,names
import subprocess

import logging
logging.basicConfig(filename='system.log',
	filemode='a',
	format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
	datefmt='%H:%M:%S',
	level=logging.DEBUG)
logger = logging.getLogger('tkpiece')

def pack(uid,topic,data):
	''' Takes 3 arguments, the content of the third is data or none '''
	if data is None:
		return uid+' '+topic
	else:
		return uid+' '+topic+' '+bytes(data)

def unpack(msg):
	''' Returns a well-formed message or None '''
	if msg is not None:
		parts = msg.split(' ',2)
		if len(parts) == 3:
			return tuple(parts)
		elif len(parts) == 2:
			return (parts[0],parts[1],None)
	return (None,None,None)

def is_valid_msg_(well_formed_packet_tuple):
	''' Checks if a packet represents a vaild outgoing message '''
	uid,topic,data = well_formed_packet_tuple
	if uid not in names(Uid):
		print('['+str(uid)+'] not valid Uid in wtfj_ids.py')
		return False
	if topic not in names(Msg):
		print('['+str(topic)+'] not valid Msg in wtfj_ids.py')
		return False
	return True

def is_valid_req_(well_formed_packet_tuple):
	''' Checks if a packet represents a vaild incoming request '''
	to_uid,topic,data = well_formed_packet_tuple
	uid = to_uid[1:]
	if uid not in names(Uid):
		print('['+str(uid)+'] not valid Uid in wtfj_ids.py')
		return False
	if topic not in names(Req):
		print('['+str(topic)+'] not valid Req in wtfj_ids.py')
		return False
	return True

def make_color(r_uint8,g_uint8,b_uint8):
	''' Color in 24-bit RGB format to '0x#######' string format '''
	r = '0x{:02x}'.format(r_uint8).replace('0x','')
	g = '0x{:02x}'.format(g_uint8).replace('0x','')
	b = '0x{:02x}'.format(b_uint8).replace('0x','')
	return '#'+r+g+b
	

if __name__ == '__main__': # Little bit of testing 
	
	# Check the validity of unpacking msg and req signals
	assert is_valid_req_(unpack('@test stop'))
	assert is_valid_req_(unpack('@test stop '))
	assert is_valid_req_(unpack('@test stop  as$#%WT$ saf 3'))
	assert is_valid_msg_(unpack('test idle'))
	assert is_valid_msg_(unpack('test idle adsfjwljlk234asdf asdfA'))
	assert is_valid_req_(unpack('@test err')) == False
	assert is_valid_msg_(unpack('@test ')) == False
	assert is_valid_msg_(unpack('@test')) == False
	print('--Tests passed--')