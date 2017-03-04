from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(ZPrinter,argv)

class ZPrinter(Piece):
	@staticmethod
	def script(): return Script(['@zprinter marco','@zprinter stop'])

if __name__ == '__main__': main()