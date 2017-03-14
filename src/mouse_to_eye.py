from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(Mouse_to_Eye,argv,[Uid.TKPIECE])

class Mouse_to_Eye(Piece):

	def _ON_tkpiece_mouse(self,data):
		self._out.send('eyetracker gaze '+data)

	@staticmethod
	def script():
		script = [
			'@mouse_to_eye marco',
			'tkpiece mouse 0.3,0.5',
			'@mouse_to_eye stop'
		]
		return Script(script)

if __name__ == '__main__': main()