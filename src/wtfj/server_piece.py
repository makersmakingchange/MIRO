from client_piece import *
from wtfj_assert import *
import os

class ServerPiece(object):
	def __init__(self,echo=True,silent=False):
		self._pull = Queue()
		self._pub = {}
		self._echo = echo
		self._silent = silent
		for uid in names(Uid):
			self._pub[uid] = Queue()

	def send_string(self,string):
		''' Sends a string to this server '''
		self._pull.put(string)
		try:
			Uid = string.split(' ',1)[0]
		except KeyError:
			pass

	def recv_string(self,uid,wait=None):
		''' Returns a string in this server's buffer '''
		ret = None
		try:
			ret = self._pub[uid].get(block=(wait != DONTWAIT))
		except Empty:
			pass # No message in queue
		except KeyError:
			self.publish('server err ['+str(uid)+'] not in subscriber list')
			self.publish('server err FATAL server stopping all clients and quitting')
			self.hit_it_and_quit_it()
		return ret

	def await(self,topic,command=None,wait_sec=0):
		''' Waits for a specific command from a specific topic '''
		start = time.clock()
		while True:
			if time.clock() - start > wait_sec:
				if wait_sec is not 0:
					self.publish('server err timed out waiting for ['
						+str(topic)+' '+str(command)+']')
					return None
			response = self.poll(timeout_sec=0.001)
			if response is not None:
				msg_parts = response.split(' ',2)
				if msg_parts[0] == topic:
					if command is not None and msg_parts[1] == command:
						return response


	def publish(self,string):
		''' Puts message in outgoing queue for all '''
		for key in self._pub:
			self._pub[key].put(string)
		self._print('sent',string)

	def send_to(self,uid,req,data=''):
		''' Puts message in outgoing queue for single Piece '''
		if data is '': 
			msg = '@'+uid+' '+req
		else:
			msg = '@'+uid+' '+req+' '+data
		self._pub[uid].put(msg)
		self._print('sent',msg)

	def poll(self,timeout_sec=1):
		''' Returns one message in incoming queue '''
		try:
			msg = self._pull.get(block=True,timeout=timeout_sec)
			self._print('recv',msg)
			if self._echo == True:
				for key in self._pub:
					self._pub[key].put(msg)
				self._print('echo',msg)
			return msg
		except Empty:
			return None

	def subscribe(self,topic):
		pass

	def _print(self,prompt,msg):
		if self._silent is False: print(prompt.upper()+' > '+msg)

	def hit_it_and_quit_it(self,nuclear=False):
		self.publish('server stopping ATTEMPTING TO STOP ALL PIECES')
		for key in member_names(Uid):
			self.send_to(key,Req.STOP)
			self.await(key,Msg.STOPPING,0.1)
		if nuclear == True:
			self.publish('server stopping ATTEMPT SHUTDOWN ALL PYTHON PROCESSES')
			while True:
				os.system("taskkill /im python.exe")	
		else:
			quit()

if __name__ == '__main__': # Do some light testing
	
	# Create a client and a server 
	cli = ClientPiece(Uid.TEST)
	serv = ServerPiece()

	# Start the client
	# Client uses the server's [send_string] & [recv_string] methods
	cli.start(serv,serv)
	
	# Send string to everyone in Uid list
	serv.publish('id topic [data_in whatever format]')

	# send structured message to one client
	serv.send_to('test','some_topic','some data')

	# Send structured message without data to one client
	serv.send_to(Uid.TEST,Req.MARCO)
	# Wait forever for this response to be received
	Assert(serv.await(Uid.TEST,Msg.POLO)).not_equal(None)

	# Send structured message with data to one client
	serv.send_to(Uid.TEST,Msg.SIZE,'0,1')
	# Wait for err response 1 second
	serv.await(Uid.TEST,Msg.ERR,wait_sec=1)
	# Wait 1 sec for response that never comes
	serv.await(Uid.TEST,'no_response_expected',wait_sec=1)

	serv.hit_it_and_quit_it()