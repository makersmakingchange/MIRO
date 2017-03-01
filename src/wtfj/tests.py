''' Testing playground '''
''' Auth: max@embeddedprofessional.com '''

from server_piece import *
from client_piece import *
from wtfj_assert import Assert


class GuiAskerPiece(ClientPiece):
	''' Asks the gui for size, sends acknowledgement when received, stops '''
	def _after_start(self):
		self.size = None
		self.subscribe(Uid.GUI)
		self.send_to(Uid.GUI,Req.GET,Msg.SIZE)

	def _on_gui_size(self,data=None):
		self.size = [int(x) for x in data.split(',')]
		self.send(Msg.ACK,str(self.size))
		self.stop()


class MockGuiPiece(ClientPiece):
	''' Sends out its size when queried '''
	def _on_get(self,data=''):
		if data == Msg.SIZE:
			self.send(Msg.SIZE,'1280,800')
			return
		self.err('get for variable ['+data+'] failed')


class SlowPoke(ClientPiece):
	def _on_start(self):
		time.sleep(1)
		self.send(Msg.STARTED)

	def _before_stop(self):
		time.sleep(1)


if __name__ == '__main__': # Test a few different clients 
	# Start a local loopback server
	serv = ServerPiece(echo=True)

	# Start a slow client, check that we execute blocking poll properly
	SlowPoke(Uid.TEST).start(serv,serv)
	response = serv.poll()
	Assert(response).topic_is(Msg.STARTED)

	# Check of another client started
	MockGuiPiece(Uid.GUI).start(serv,serv)
	response = serv.poll()
	Assert(response).sent_by(Uid.GUI).topic_is(Msg.STARTED)

	# Send request for response from gui
	serv.send_to(Uid.GUI,Req.MARCO)
	response = serv.poll()
	Assert(response).topic_is(Msg.POLO)

	# Publish to all, wait for a response that matches uid gui and topic polo
	serv.publish('@gui marco')
	response = serv.await(Uid.GUI,Msg.POLO)
	Assert(response).not_equal(None)
	Assert(response).equals('gui polo')

	# Send an erroneous packet
	serv.publish('@gui get my lunch')
	response = serv.poll()
	Assert(response).sent_by(Uid.GUI).topic_is(Msg.ERR)
	
	# Request a variable
	serv.publish('@gui get size')
	response = serv.poll()
	Assert(response).sent_by(Uid.GUI).contains(Msg.SIZE)

	# If we got here we good, kill all python processes
	Assert.success()
	serv.hit_it_and_quit_it(nuclear=True)

