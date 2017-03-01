
class Connector(object):
	''' Connects a client or server to i/o '''

	def send(self,string):
		raise NotImplementedError

	def poll(self,wait_s=1,uid=None):
		''' Must return a list of messages '''
		raise NotImplementedError

	def subscribe(self,uid):
		raise NotImplementedError
	