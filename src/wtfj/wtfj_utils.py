from __future__ import division
from wtfj_ids import *
import subprocess
import time

def distance(x1,y1,x2,y2):
	''' Returns float representing 2D Euclidean distance '''
	return ((x1-x2)**2 + (y1-y2)**2)**0.5

def normalize(*vector_components):
	''' Returns a vector of len(vector_components) size normalized to 1 '''
	l = length(*vector_components)
	return [x/l for x in vector_components]

def length(*vector_components):
	return sum([x**2 for x in vector_components])**0.5

def ensure_delimited(uid):
	''' Takes a string and adds an @ delimiter if one not there already'''
	return uid if uid[0] == '@' else '@'+uid

def nuclear_option():
	''' Attempts to kill all python processes '''
	import os
	for i in range(20):
		print('nuke '+str(i))
		os.system("taskkill /im python.exe")
	quit()

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

def pack_csv(*args):
	''' Returns a string of values seperated by commas '''
	data = ''
	for arg in args:
		data += (str(arg)+',')
	data = data[:-1]
	return data

def is_valid_msg_(well_formed_packet_tuple):
	''' Checks if a packet represents a vaild outgoing message '''
	uid,topic,data = well_formed_packet_tuple
	if uid not in get_attr(Uid):
		print('['+str(uid)+'] not valid Uid in wtfj_ids.py')
		return False
	if topic not in get_attr(Msg):
		print('['+str(topic)+'] not valid Msg in wtfj_ids.py')
		return False
	return True

def is_valid_req_(well_formed_packet_tuple):
	''' Checks if a packet represents a vaild incoming request '''
	to_uid,topic,data = well_formed_packet_tuple
	uid = to_uid[1:]
	if uid not in get_attr(Uid):
		print('['+str(uid)+'] not valid Uid in wtfj_ids.py')
		return False
	if topic not in get_attr(Req):
		print('['+str(topic)+'] not valid Req in wtfj_ids.py')
		return False
	return True

def make_color(r_uint8,g_uint8,b_uint8):
	''' Color in 24-bit RGB format to '0x#######' string format '''
	r = '0x{:02x}'.format(r_uint8).replace('0x','')
	g = '0x{:02x}'.format(g_uint8).replace('0x','')
	b = '0x{:02x}'.format(b_uint8).replace('0x','')
	return '#'+r+g+b


class RecordKeeper(object):
	''' Saves historical records for a given number of seconds
	Also provides functions to calculate statistics of those records
	The first value of a record is always the time it was added '''
	
	def __init__(self,time_to_keep_record_s):
		''' Sets length to keep a record for and initializes record storage '''
		self.set_timeout(time_to_keep_record_s)
		self._history = []

	def add_record(self,*values):
		''' Adds a new value to the history, cleans up old values '''
		t = time.clock()
		record = [t]
		for val in values:
			record.append(val)
		self._history.append(record)
		self._history = filter(lambda record: (t-record[0] < self._record_timeout),self._history)

	def set_timeout(self,timeout_s):
		self._record_timeout = timeout_s

	def mean(self):
		''' Returns mean of record values over _record_timeout seconds '''
		return map(lambda x: sum(x)/len(x), zip(*self._history))

	def one_norm(self):
		''' Returns mean of record values over _record_timeout seconds '''
		return map(lambda x: sum([abs(val) for val in x])/len(x), zip(*self._history))

	def first_derivative(self):
		''' Returns list of records of change in record vector over change in time '''
		dh_dt = []
		for i in range(1,len(self._history)):
			t = self._history[i][0]
			dt = t-self._history[i-1][0]
			d_record = []
			d_record.append(t)
			for j in range(1,len(self._history[i])):
				dv_dt = (self._history[i][j]-self._history[i-1][j])/dt
				d_record.append(dv_dt)
			dh_dt.append(d_record)
		return dh_dt

	def get_history(self):
		return self._history

	def set_history(self, *values):
		'''Sets all of the values in the history to a provided values'''
		for record in self._history:
			for x in range(0,len(values)):
				record[x+1] = values[x]


if __name__ == '__main__': # Little bit of testing 

	# Check the validity of unpacking msg and req signals
	assert is_valid_req_(unpack('@piece stop'))
	assert is_valid_req_(unpack('@piece stop '))
	assert is_valid_req_(unpack('@piece stop  as$#%WT$ saf 3'))
	assert is_valid_msg_(unpack('piece idle'))
	assert is_valid_msg_(unpack('piece idle adsfjwljlk234asdf asdfA'))
	assert is_valid_msg_(unpack('@piece err')) == False
	assert is_valid_msg_(unpack('@piece ')) == False
	assert is_valid_msg_(unpack('@piece')) == False
	
	# Check that vector normalization works
	v = [3,4]
	v_norm = normalize(*v)
	assert v_norm[0] == 0.6
	assert v_norm[1] == 0.8

	# Check that the recordkeeper correctly stores values and performs functions
	r = RecordKeeper(1.0)
	r.add_record(-1000,1000)
	time.sleep(2.0)
	r.add_record(0,1)
	time.sleep(0.25)
	r.add_record(-2,3)
	time.sleep(0.25)
	r.add_record(-4,2)
	mean = r.mean()
	assert mean[1] == -2.0
	assert mean[2] == 2.0
	print(r.first_derivative()[0], "Record derivative should be around 2.0,-8.0,8.0")

	print('[Tests passed]')