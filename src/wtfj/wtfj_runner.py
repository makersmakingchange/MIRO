from connectors_local import *
from connectors_zmq import *
from wtfj_ids import *
import subprocess

SCRIPT_PATH = '../scripts/'

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
			else:
				subprocess.Popen(args)
	
	@staticmethod
	def run_w_cmd_args(Class,argv,subscriptions=[]):
		print_bar('Running with args '+repr(argv))
		try:
			mode = argv[1]
		except IndexError as e:
			mode = Mode.TEST

		if mode == Mode.TEST:
			setup = [ 

				Class.script(), # Executes default test script
				Printer('[<] '),
				False

			]

		if mode == Mode.ZPRINTER:
			zmqs = ZmqSubscriber()
			for uid in get_attr(Uid):
				zmqs.subscribe(uid)
			setup = [ 

				zmqs, # All msgs going to piece
				Printer('[<] '), # Coming from piece
				True # Local echo on

			]

		if mode == Mode.ZCONSOLE:
			setup = [ 

				Console('[>] '), # User input in _DURING_poll function of ZConsole
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

		cnx_line = '['+repr(to_piece.__class__.__name__)+']--->['+repr(Class.__name__)+']--->['+repr(from_piece.__class__.__name__)+']'

		print_bar('Connecting to '+repr(Class.__name__).lower())
		print_bar(cnx_line)

		piece = Class(to_piece,from_piece,echo=local_echo)
		print('Echo is '+str(local_echo))

		for subscription in subscriptions:
			piece.subscribe(subscription)
		piece.start()