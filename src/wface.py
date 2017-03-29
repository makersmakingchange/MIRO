from wtfj import *
from tkpiece import TkPiece


def main():
	from sys import argv
	Runner.run_w_cmd_args(WFace,argv)


class WFace(Piece):
	''' Was a Tk window, now just calculates values '''
	def _AFTER_start(self):
		''' Subscribe to Face piece (c++ exe) and create record storage '''
		self.subscribe(Uid.FACE)
		self._face_record = RecordKeeper(1)
		self._metric_record = RecordKeeper(1)
		self._noise_record = RecordKeeper(1)
		self._brow = False
		self._mouth = False

	def _ON_face_position(self,data):
		''' Calculate whether eyebrows have been raised and mouth opened '''
		vals = [float(n) for n in data.split(',')]
		d_rbrow = distance(vals[0],vals[1],vals[14],vals[15])
		d_lbrow = distance(vals[2],vals[3],vals[14],vals[15])
		d_nose  = distance(vals[8],vals[9],vals[14],vals[15])
		self._face_record.add_record(d_rbrow,d_lbrow,d_nose)
		dface_dt = self._face_record.first_derivative()
		self.send_to(Uid.TKPIECE,Msg.TEXT,pack_csv('feedback',dface_dt[1],dface_dt[2],dface_dt[3]))

	def _ON_face_vector(self,data):
		vals = [float(n) for n in data.split(',')]
		self._face_record.add_record(*vals)
		dface_dt = self._face_record.first_derivative()
		neither_brow_nor_mouth = [dface_dt[0][1],dface_dt[0][2],dface_dt[0][3]]
		l = length(*neither_brow_nor_mouth)
		self._noise_record.add_record(l)
		
		brow_metric = dface_dt[0][1]
		mouth_metric = dface_dt[0][5]

		self._metric_record.add_record(brow_metric)
		
		noise_1norm = self._noise_record.one_norm()
		metric_1norm = self._metric_record.one_norm()
		#self.send(Msg.TEXT,pack_csv(metric,metric_1norm[1],noise_1norm[1]))
		
		if l < 0.25:
			if brow_metric > 0.08 and brow_metric/l > 0.7:
				if self._brow == False:
						self._out.send('brow '+Msg.SELECT+'         '+pack_csv(l))
						self._brow = True
			else:
				self._brow = False

			if mouth_metric > 0.08 and mouth_metric/l > 1.0:
				if self._mouth == False:
						self._out.send('mouth '+Msg.SELECT+'        '+pack_csv(l))
						self._mouth = True
			else:
				self._mouth = False
		
		#self.send_to(Uid.TKPIECE,Msg.TEXT,pack_csv('feedback',*dface_dt))
				
	@staticmethod
	def script():
		script = [
			'@wface marco',
			'@wface period 0.2',
			'face position 200,200,300,200,200,300,400,200,300,250,250,100,100,300,100,200',
			'face position 200,200,300,200,200,300,400,200,300,250,250,100,100,300,100,200',
			'face position 200,200,300,200,200,300,400,200,300,250,250,100,100,300,100,200',
			'face position 200,200,300,200,200,300,400,200,300,250,250,100,100,300,100,200',
			'face position 250,250,350,250,200,300,400,200,300,250,250,100,100,300,100,200',
			'face position 250,250,350,250,200,300,400,200,300,250,250,100,100,300,100,200',
			'face vector 5.01,0,350,250,200,300',
			'@wface wait 0.1',
			'face vector 250,250,350,250,200,300',
			'@wface wait 0.2',
			'face vector 250,250,350,250,200,300',
			'@wface wait 0.3',
			'face vector 250,250,350,250,200,300',
			'@wface stop'
		]
		return Script(script)

if __name__ == '__main__': main()