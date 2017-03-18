from wtfj import *
from tkpiece import TkPiece


def main():
	from sys import argv
	Runner.run_w_cmd_args(WFace,argv)

def distance(x1,y1,x2,y2):
	return ((x1-x2)**2 + (y1-y2)**2)**0.5


class WFace(Piece):
	''' Was a Tk window, now just calculates values '''
	def _AFTER_start(self):
		self.subscribe(Uid.FACE)
		self._history = []
		self._score_history = []
		self._face_vel_history = []
		self._brow = False

	def _ON_face_position(self,data):
		''' Calculate whether eyebrows have been raised and mouth opened '''
		vals = [float(n) for n in data.split(',')]
		now = time.clock()

		avg_face_velocity = 0
		try:
			last_time = self._val_history[0]
			last_vals = self._val_history[1]
			n = int(len(last_vals)/2)
			for i in range(n):
				i_x = 2*i
				i_y = 2*i+1
				avg_face_velocity += distance(last_vals[i_x],last_vals[i_y],vals[i_x],vals[i_y])
			avg_face_velocity /= n
			avg_face_velocity /= (now - last_time)
		except AttributeError as e:
			pass # No last values found
		self._val_history = [now,vals]

		num_parts = int(len(vals)/2)
		x_vals = vals[::2]
		y_vals = vals[1::2]
		face_x,face_y = sum(x_vals)/num_parts,sum(y_vals)/num_parts
		std_dev_x = (sum([(x - face_x)**2 for x in x_vals])/num_parts)**0.5
		std_dev_y = (sum([(y - face_y)**2 for y in y_vals])/num_parts)**0.5
		std_dev = (std_dev_x**2 + std_dev_y**2)**0.5

		brow_to_eye_distance_r = distance(vals[0],vals[1],vals[4],vals[5])
		brow_to_eye_distance_l = distance(vals[2],vals[3],vals[6],vals[7])
		mouth_distance = distance(vals[10],vals[11],vals[12],vals[13])

		brow_score = (brow_to_eye_distance_r/std_dev + brow_to_eye_distance_l/std_dev)/2
		mouth_score = (mouth_distance/std_dev)
		
		self._history = self._history[-99:]
		record = [now,brow_score,mouth_score]
		self._history.append(record)
		
		# Calculate average brow score over the last second
		i,avg = 0,0
		while True:
			if i+1 > len(self._history): 
				break
			t = self._history[-(i+1)][0]
			if now - t > 1.0: 
				break
			avg += self._history[-(i+1)][1]
			i += 1
		avg /= i
		
		brow_score -= avg

		score_record = [now,brow_score]
		self._score_history = self._score_history[-99:]
		self._score_history.append(score_record)

		# Calculate area above the average for last second
		i,area = 0,0
		while True:
			if i+2 > len(self._score_history): 
				break
			t = self._score_history[-(i+1)][0]
			if now - t > 1.0: 
				break
			delta = t - self._score_history[-(i+2)][0]
			area += delta*self._score_history[-(i+2)][1]
			i += 1

		face_vel_score = avg_face_velocity/std_dev

		face_vel_record = [now,face_vel_score]
		self._face_vel_history = self._face_vel_history[-99:]
		self._face_vel_history.append(face_vel_record)

		# Calculate average face velocity over the last second
		i,face_vel = 0,0
		while True:
			if i+1 > len(self._face_vel_history): 
				break
			t = self._face_vel_history[-(i+1)][0]
			if now - t > 1.0: 
				break
			face_vel += self._face_vel_history[-(i+1)][1]
			i += 1
		face_vel /= i

		if face_vel < 0.5:
			if area > 0.01:
				if self._brow == False:
					self._brow = True		
					self.send(Msg.SELECT)
			else:
				self._brow = False

	@staticmethod
	def script():
		script = [
			'@wface marco',
			'@wface period 0.2',
			'face position 200,200,300,200,200,300,400,200,300,250,250,100,100,300',
			'face position 200,200,300,200,200,300,400,200,300,250,250,100,100,300',
			'face position 200,200,300,200,200,300,400,200,300,250,250,100,100,300',
			'face position 200,200,300,200,200,300,400,200,300,250,250,100,100,300',
			'face position 250,250,350,250,200,300,400,200,300,250,250,100,100,300',
			'face position 250,250,350,250,200,300,400,200,300,250,250,100,100,300',
			'face position 250,250,350,250,200,300,400,200,300,250,250,100,100,300',
			'face position 250,250,350,250,200,300,400,200,300,250,250,100,100,300',
			'@wface stop'
		]
		return Script(script)

if __name__ == '__main__': main()