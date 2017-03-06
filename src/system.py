from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(System,argv)

class System(Piece):

	def _DURING_poll(self):
		time.sleep(0.01)

	def _BEFORE_stop(self):
		for uid in get_attr(Uid):
			if uid != self._uid:
				self.send_to(uid,Req.STOP)
		time.sleep(1)

	def _ON_start(self,data):
		try:
			piece,mode = data.split()
		except ValueError:
			piece,mode = data,Mode.ZCLIENT
		Runner.run(piece,mode)

	def _ON_nuke(self,data):
		wtfj_utils.nuclear_option()

	def _ON_script(self,data):
		filename = SCRIPT_PATH+data+'.txt'
		with open(filename) as f:
			for line in f:
				parts = line.split(' ',1)
				if parts[0] == 'start':
					self._ON_start(parts[1])
				else:
					line = line.split('\n')[0]
					self._out.send(line)

	@staticmethod
	def script(): return Script(['@system stop'])

if __name__ == '__main__': main()