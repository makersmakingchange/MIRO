from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(Position_Cursor,argv)

class Position_Cursor(Piece):
	''' Shows position of eyetracker/mouse on the screen '''
	def _BEFORE_start(self):
		self.subscribe(Uid.EYETRACKER)
	
	def _AFTER_start(self):
		self._handle = 'cursor'
		self._color = make_color(100,100,255)
		self._radius = 50
		self.send_to(Uid.TKPIECE,Req.CREATE,pack_csv('circle',self._handle,0.5,0.5,self._radius,self._color))

	def _ON_eyetracker_gaze(self,data):
		x,y = data.split(',')
		x,y = float(x),float(y)
		self.send_to(Uid.TKPIECE,Req.POSITION,pack_csv(self._handle,x,y,self._radius))

	@staticmethod
	def script():
		script = [
			'@position_cursor marco',
			'eyetracker gaze 0.46,0.56',
			'@position_cursor wait 1',
			'@position_cursor stop'
		]
		return Script(script)


if __name__ == '__main__': main()
