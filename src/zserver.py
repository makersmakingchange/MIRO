from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(ZServer,argv)

class ZServer(Piece):
	def _DURING_poll(self):
		self.send_to('zprinter','marco')
		self.send_to('zpconsole','marco')
		time.sleep(0.1)

	@staticmethod
	def script(): return Script(['@zserver marco','@zserver stop'])

if __name__ == '__main__': main()