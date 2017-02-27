class ClientPiece(object):
	def __init__(self,Uid):
		self._Uid = Uid
		self.ERR = 'err'
		self.STOP_MSG = 'stopping'
		self.START_MSG = 'started'
		self._on_start()

	def send(self,topic,data=''):
		print(self._Uid+' '+topic+' '+data)

	def _on_stop(self,data=None):
		self.send(self.STOP_MSG)
		quit()

	def _on_start(self,data=None):
		self.send(self.START_MSG)

	def _interpret(self,msg):
		parts = msg.split()
		try:
			size = len(parts)
			if size < 2 or size > 3:
				self.send(self.ERR,'malformed message ['+msg+'], found '+str(size)+' of minimum 2 maximum 3 arguments')
			else:
				if parts[0] != '@'+self._Uid:
					if size == 3:
						getattr(self,'_on_'+parts[0]+'_'+parts[1])(parts[2])
					else:
						getattr(self,'_on_'+parts[0]+'_'+parts[1])()
				else:
					if size == 3:
						getattr(self,'_on_'+parts[1])(parts[2])
					else:
						getattr(self,'_on_'+parts[1])()
		except AttributeError as e:
			self.send(self.ERR,'no interpretation of command '+parts[1])

class MyPiece(ClientPiece):
	def _on_foo(self,data=None):
		if data == None:
			self.send('foo')
		else:
			self.send('foo','with data '+data)

	def _on_bar(self):
		self.send('BARDYBARBAR')

	def _on_gui_size(self,data=None):
		self.send('size '+str(data)+' received')

mp = MyPiece('mp')
mp._interpret('@mp foo')
mp._interpret('@mp')
mp._interpret('@mp holy_moly')
mp._interpret('@mp trashman DEALWITHIT')
mp._interpret('@mp foo DATADATA')
mp._interpret('gui size 1280,720')
mp._interpret('@mp bar')
mp._interpret('@mp stop')