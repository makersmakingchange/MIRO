from connectors_local import *
from connectors_zmq import *
from wtfj_ids import *
import subprocess

class Runner:

	@staticmethod
	def run(uid,mode=Mode.TEST):
		if mode == Mode.EXE: 
			args = ['../bin/'+uid+'/'+uid+'.exe',Mode.EXE]
			subprocess.Popen(args)
		elif mode == Mode.CONSOLE:
			args = ['python',uid+'.py',Mode.CONSOLE]
			subprocess.Popen(args,creationflags=subprocess.CREATE_NEW_CONSOLE)
		elif mode == Mode.SERVER_ZMQ:
			args = ['python',uid+'.py',Mode.SERVER_ZMQ]
			subprocess.Popen(args)
		elif mode == Mode.CLIENT_ZMQ:
			args = ['python',uid+'.py',Mode.CLIENT_ZMQ]
			subprocess.Popen(args)
		else:
			args = ['python',uid+'.py',Mode.TEST]
			subprocess.Popen(args)
	
	@staticmethod
	def run_w_cmd_args(PieceClass,argv,subscriptions=[]):
		print('running with args '+repr(argv))
		if len(argv) == 1:
			print(__file__+' not supplied mode arg, running in Mode.TEST')
			argv = [argv[0],Mode.TEST]
		if argv[1] == Mode.CONSOLE:
			piece = PieceClass(Console('[>] '),Printer('[<]' ))
			for subscription in subscriptions:
				piece.subscribe(subscription)
			piece.start()
		elif argv[1] == Mode.CLIENT_ZMQ:
			zsub = ZmqSubscriber() # Filters incoming messages to uid 'test'
			zpush = ZmqPusher() # Pushes messages back to server
			piece = PieceClass(zsub,zpush)
			for subscription in subscriptions:
				piece.subscribe(subscription)
			piece.start()
		elif argv[1] == Mode.SERVER_ZMQ:
			zpub = ZmqPublisher()
			zpull = ZmqPuller()
			piece = PieceClass(zpull,zpush,echo=True)
			for subscription in subscriptions:
				piece.subscribe(subscription)
			piece.start()
		elif argv[1] == Mode.TEST:
			script = PieceClass.get_test_script()
			piece = PieceClass(Script(script),Printer('PIECE RECV < ' ))
			for subscription in subscriptions:
				piece.subscribe(subscription)
			piece.start()
		else:
			print(' mode arg ['+argv[1]+'] is invalid, aborting run')
