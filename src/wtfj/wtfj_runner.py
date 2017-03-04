from connectors_local import *
from connectors_zmq import *
from wtfj_ids import *
import subprocess

class Runner:

	@staticmethod
	def run(uid,mode=None):
		if mode == None:
			mode = uid
		if mode == Mode.EXE: 
			args = ['../bin/'+uid+'/'+uid+'.exe',Mode.EXE]
			subprocess.Popen(args)
		else:
			args = ['python',uid+'.py',mode]
			if mode in [Mode.INTERACTIVE,Mode.ZCONSOLE,Mode.ZPRINTER]:
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
			setup = [ 

				PieceClass.script(), # Executes default test script
				Printer('[<] '),
				False 

			]
			if mode == Mode.ZPRINTER:
				zmqs = ZmqSubscriber()
				for uid in names(Uid):
					zmqs.subscribe(uid)
				setup = [ 

					zmqs, # All msgs going to piece
					Printer('[<] '), # Coming from piece
					True # Local echo on

				]
			if mode == Mode.ZCONSOLE:
				print('SDFA')
				setup = [ 

					Console('[>] '), # User input
					ZmqPusher(), # Gets passed to network
					True # Local echo on

				]
			if mode == Mode.ZCLIENT: 
				setup = [ 

					ZmqSubscriber(), # Going to piece from a ZmqPublisher
					ZmqPusher(), # Pushing to ZmqPuller
					False 

				]
			if mode == Mode.ZSERVER:
				setup = [ 

					ZmqPuller(), # Pulls from all ZmqPushers
					ZmqPublisher(), # Publishes to all ZmqSubscribers
					True

				]
			if mode == Mode.INTERACTIVE:
				setup = [ 

					Console('[>] '), # Keyboard input
					Printer('[<] '), # Stdout output
					False # Local echo of piece 
				]
	
			to_piece   = setup[0] 
			from_piece = setup[1] 
			local_echo = setup[2]

			print('----')
			print('Connecting to ['+repr(PieceClass.__name__)+']')
			print('<---')
			print('['+repr(to_piece.__class__.__name__)+']')
			print('--->')
			print('['+repr(from_piece.__class__.__name__)+']')
			print('----')

			piece = PieceClass(to_piece,from_piece,echo=local_echo)
			print('Echo is '+str(local_echo))

			for subscription in subscriptions:
				piece.subscribe(subscription)
			piece.start()
		else:
			print(' mode arg ['+argv[1]+'] is invalid, aborting run')