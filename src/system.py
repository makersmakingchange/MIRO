from wtfj import *
from threading import Lock
import datetime

def main():
	from sys import argv
	Runner.run_w_cmd_args(System,argv)

LOG_PATH = '../log/'

# Open log file for appending
log_name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.txt'
log = open(LOG_PATH+log_name,'w+')
log_lock = Lock()

def log_write(msg):
	log_lock.acquire()
	log_msg = str(time.clock())+' '+msg+'\n'
	log.write(log_msg)
	log_lock.release()


class System(Piece):

	# This function masks inherited functionality in Piece
	def send(self,topic,data=None):
		''' Sends a message string to the connector '''
		try:
			msg = pack(self._uid,topic,data)
			log_write(msg)
			self._out.send(msg)
		except AssertionError as e:
			self.err('Uid or topic invalid for msg ['+str(topic)+']['+str(data)+']\n'+repr(e))

	# This function masks inherited functionality in Piece
	def send_to(self,uid,topic,data=''):
		''' Sends a message string targeted for a specific client or service '''
		''' The connector bears responsibility for proper routing '''
		uid = ensure_delimited(uid)
		try:
			msg = pack(uid,topic,data)
			log_write(msg)
			self._out.send(msg)
		except AssertionError as e:
			self.err('Uid or topic invalid for msg ['+str(topic)+']['+str(data)+']\n'+repr(e))
		return self

	# This function masks inherited functionality in Piece
	def _poll(self):
		''' Run in its own thread '''
		while self._alive == True:
			# Loop through all new available messages
			msgs = self._in.poll(uid=self._uid,wait_s=self._period)
			for msg in msgs: 
				# Process each message
				if self._interpret(msg) == False:
					# Echo back out if can't consume it and _echo is set
					if self._echo == True: 
						self._out.send(msg)
				log_write(msg)
			try:
				self._DURING_poll()
			except AttributeError:
				pass

	def _BEFORE_stop(self):
		for uid in get_attr(Uid):
			if uid != self._uid:
				self.send_to(uid,Req.STOP)
			time.sleep(0.1)

	def _ON_start(self,data):
		try:
			piece,mode = data.split()
		except ValueError:
			piece,mode = data,Mode.ZCLIENT
		Runner.run(piece,mode)

	def _ON_nuke(self,data):
		wtfj_utils.nuclear_option()

	def _ON_script(self,data):
		filename = SCRIPT_PATH+data+'.txt'
		with open(filename) as f:
			for line in f:
				line = line.split('\n')[0]
				#if self._uid in line.split()[0]:
				if not self._interpret(line):
					self._out.send(line)

	@staticmethod
	def script(): return Script(['@system stop'])

if __name__ == '__main__': main()