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

	def _ON_nuke(self,data):
		wtfj_utils.nuclear_option()

	@staticmethod
	def script(): return Script(['@system marco','@system stop'])

if __name__ == '__main__': main()