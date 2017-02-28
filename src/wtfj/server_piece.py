from client_piece import *

class ServerPiece(object):
	def __init__(self,echo=False):
		self._pull = Queue()
		self._pub = {}
		self._echo = echo

	def add_subscriber(self,Uid):
		self._pub[Uid] = Queue()

	def send_string(self,string):
		''' Sends a string to this server '''
		self._pull.put(string)
		try:
			Uid = string.split(' ',1)[0]
		except KeyError:
			pass

	def recv_string(self,args=None,Uid=None):
		''' Returns a string in this server's buffer '''
		ret = None
		try:
			ret = self._pub['@'+Uid].get(block=(args != DONTWAIT))
		except Empty:
			pass # No message in queue
		except KeyError:
			self.publish('server err '+Uid+' subscriber not in list')
		return ret

	def publish(self,string):
		''' Puts message in outgoing queue '''
		for key in self._pub:
			self._pub[key].put(string)
		print('published> '+string)

	def pull(self,args=None,timeout_s=0):
		''' Returns messages in incoming queue '''
		string = self._pull.get(block=(args != DONTWAIT),timeout=timeout_s)
		print('received< '+string)
		if self._echo == True:
			for key in self._pub:
				self._pub[key].put(string)
			print('echoed> '+string)
		return string

	def poll(self,n=1):
		t_s = 0.100
		if n == 1:
			return self.pull(timeout_s=t_s) 
		else:
			msgs = []
			for i in range(n):
				msgs.append(self.pull(timeout_s=t_s))
			return msgs