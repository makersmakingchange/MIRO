from server_piece import *
from client_piece import *
from wtfj_assert import Assert


class MyPiece(ClientPiece):
	def _on_foo(self,data=None):
		if data == None:
			self.send('foo')
		else:
			self.send('foo','with data '+data)

	def _after_start(self):
		self.size = None
		self.add_interest(Uids.GUI)
		self.send('[_after_start]','-this function called after successful start of piece')
		self.send_to(Uids.GUI,'get','size')

	def _on_bar(self):
		self.send('BARDYBARBAR')

	def _before_stop(self):
		self.send('[_before_stop]','-this function called before attempting to stop piece')

	def _on_gui_size(self,data=None):
		self.size = [int(x) for x in data.split(',')]


class MockGuiPiece(ClientPiece):
	def _on_get(self,data=''):
		if data == 'size':
			self.send('size','1280,800')
			return
		self.err('get for variable ['+data+'] failed')

if __name__ == '__main__':
	serv = ServerPiece(echo=True)
	serv.add_subscriber('@gui')
	serv.add_subscriber('@max')

	MockGuiPiece(Uids.GUI).start(serv,serv)
	Assert(serv.poll()).equals('gui started ').contains('gui')

	serv.publish('@gui marco')
	Assert(serv.poll()).contains('gui polo')

	serv.publish('@gui get my lunch')
	Assert(serv.poll()).contains('gui err')

	serv.publish('@gui get size')
	Assert(serv.poll()).contains('gui size').has_csv_array_of_size(2)

	MyPiece('max').start(serv,serv)
	Assert(serv.poll()).contains('max started')
	Assert(serv.poll()).contains('max').contains('_after_start')
	Assert(serv.poll()).equals('@gui get size')
	Assert(serv.poll()).contains('gui size')

	serv.publish('@max stop')
	Assert(serv.poll()).contains('max').contains('_before_stop')
	Assert(serv.poll()).contains('max stopping')

	serv.publish('@gui stop')
	Assert(serv.poll()).contains('gui stopping')

	