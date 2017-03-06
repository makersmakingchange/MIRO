from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(ZConsole,argv)

class ZConsole(Piece):

	#def _BEFORE_stop(self):
	#	print('Trynna stop')

	#def _DURING_poll(self):
	#	user_in = raw_input()
	#	if user_in == Msg.STOP:
	#		Piece._interpret(Msg.STOP)
	#	else:
	#		print('SENT > '+user_in)
	#		Piece._out.send(user_in)

	@staticmethod
	def script(): return Script(['@zconsole marco','@zconsole stop'])

if __name__ == '__main__': main()