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
		else:
			args = ['python',uid+'.py',mode]
			if mode == Mode.INTERACTIVE or mode == Mode.PRINTER_ZMQ:
				subprocess.Popen(args,creationflags=subprocess.CREATE_NEW_CONSOLE)
			subprocess.Popen(args)
	
	@staticmethod
	def run_w_cmd_args(PieceClass,argv,subscriptions=[]):
		print('running with args '+repr(argv))
		if len(argv) == 1:
			print(__file__+' not supplied mode arg, running in Mode.TEST')
			argv = [argv[0],Mode.TEST]
		if argv[1] in names(Mode):
			mode = argv[1]

			if mode == Mode.PRINTER_ZMQ:
				zmqs = ZmqSubscriber()
				for uid in names(Uid):
					zmqs.subscribe(uid)
				setup = [ 

					zmqs, # All msgs going to piece
					Printer('[<] '), # Coming from piece
					True # Local echo on

				]
			if mode == Mode.CLIENT_ZMQ: 
				setup = [ 

					ZmqSubscriber(), # Going to piece from a ZmqPublisher
					ZmqPusher(), # Pushing to ZmqPuller
					False 

				]
			if mode == Mode.SERVER_ZMQ:
				setup = [ 

					ZmqPublisher(), # Publishes to all ZmqSubscribers
					ZmqPuller(), # Pulls from all ZmqPushers
					True 

				]
			if mode == Mode.INTERACTIVE:
				setup = [ 

					Console('[>] '), # Keyboard input
					Printer('[<] '), # Stdout output
					True # Local echo of piece 

				]
			if mode == Mode.TEST: 
				setup = [ 

					PieceClass.script(), # Executes default test script
					Printer('[<] '),
					False 

				]
	
			to_piece   = setup[0] 
			from_piece = setup[1] 
			local_echo = setup[2]

			print(to_piece.__class__)
			print(dir(from_piece))
			piece = PieceClass(to_piece,from_piece,echo=local_echo)

			for subscription in subscriptions:
				piece.subscribe(subscription)
			piece.start()
		else:
			print(' mode arg ['+argv[1]+'] is invalid, aborting run')