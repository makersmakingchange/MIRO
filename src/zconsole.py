from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(ZConsole,argv)

class ZConsole(Piece):
	@staticmethod
	def script(): return Script(['@zconsole marco','@zconsole stop'])

if __name__ == '__main__': main()