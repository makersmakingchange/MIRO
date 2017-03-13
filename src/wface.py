from wtfj import *
from tkpiece import TkPiece

def main():
	from sys import argv
	Runner.run_w_cmd_args(WFace,argv)


def distance(x1,y1,x2,y2):
	return ((x1-x2)**2 + (y1-y2)**2)**0.5

class Pt(object):
	def __init__ (self,x,y):
		self.x = x
		self.y = y

	def __add__(self,other):
		return Pt(self.x+other.x,self.y+other.y)

	def __div__(self,scalar):
		return Pt(self.x/scalar,self.y/scalar)

	def __sub__(self,other):
		return Pt(self.x-other.x,self.y-other.y)

	def __iadd__(self,other):
		self.x += other.x
		self.y += other.y

	def __idiv__(self,scalar):
		self.x /= scalar
		self.y /= scalar

	def __imul__(self,sclar):
		self.x *= scalar
		self.y *= scalar

	def __isub__(self,other):
		self.x -= other.x
		self.y -= other.y

	def dist_to(self,other):
		return distance(self.x,self.y,other.x,other.y)

	def length(self):
		return (self.x**2+self.y**2)**0.5

class DetectedFace(object):
	def __init__(self,data):
		self.pts = [Pt(data[2*i],data[2*i+1]) for i in range(7)]
		self.birthday = time.clock()
		self.lines = []
		self.pt_txt = []
		self.vels = []
		self.vel_sum = 0
		self.colors = ['blue','red','black','black','black','yellow','green']

	def __add__(self,other):
		ret = copy.deepcopy(self)
		ret += other
		return ret

	def __sub__(self,other):
		ret = copy.deepcopy(self)
		ret -= other
		return ret

	def __iadd__(self,other):
		for i in range(len(self.pts)):
			self.pts[i] += other.pts[i]
		self.birthday += other.birthday

	def __isub__(self,other):
		for i in range(len(self.pts)):
			self.pts[i] -= other.pts[i]
		self.birthday -= other.birthday

	def __idiv__(self,scalar):
		self.pts = [self.pts / scalar]

	def r_brow(self): return self.pts[0]
	def l_brow(self): return self.pts[1]
	def r_eye(self): return self.pts[2]
	def l_eye(self): return self.pts[3]
	def nose(self): return self.pts[4]
	def up_mouth(self): return self.pts[5]
	def lo_mouth(self): return self.pts[6]

	def draw(self,canvas):
		txt = ['br','bl','er','el','n','mu','ml']
		self.pt_txt = [canvas.create_text(self.pts[i].x,self.pts[i].y,
			font=point_font,text=txt[i],fill=self.colors[i]) for i in range(len(txt))]

	def draw_difference(self,canvas,other):
		for i in range(len(self.pts)):
			self.lines.append(canvas.create_line(self.pts[i].x,self.pts[i].y,
				other.pts[i].x,other.pts[i].y,fill=self.colors[i],width=3.0))

	def calc_velocities(self,other):
		self.vels = []
		delta = self.birthday - other.birthday
		for i in range(len(self.pts)):
			pt = (self.pts[i]-other.pts[i]) / delta
			self.vels.append(pt)

	def calc_vel_differentials(self):
		#vel_sum = Pt(0,0)
		self.vel_sum = 0
		x,y = 0,0
		for vel in self.vels:
			x += vel.x
			y += vel.y
		self.vel_sum = (x**2+y**2)**0.5
		x /= len(self.vels)
		y /= len(self.vels)
		for vel in self.vels:
			vel -= Pt(x,y)

	def norm_velocities(self,scale=1):
		avg_length = self.vel_sum / len(self.vels)
		for vel in self.vels:
			vel.x = vel.x/avg_length
			vel.y = vel.y/avg_length
			vel.x = vel.x*scale
			vel.y = vel.y*scale

	def draw_velocities(self,canvas,cen_x,cen_y):
		for i in range(len(self.pts)):
			pt = self.vels[i]
			x,y = pt.x+cen_x,pt.y+cen_y
			if x**2+y**2 > (self.vel_sum / len(self.vels))**2:
				self.lines.append(canvas.create_line(cen_x,cen_y,x,y,
					fill=self.colors[i],width=3.0))

	def erase(self,canvas):
		for txt_handle in self.pt_txt:
			canvas.delete(txt_handle)
		for line_handle in self.lines:
			canvas.delete(line_handle)


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
			else:
				self._brow = False

		self.send_to(Uid.TKPIECE,Msg.TEXT,pack_csv('feedback',self._brow,area,face_vel))
		self.send(Msg.ACK)

	@staticmethod
	def script():
		script = [
			'@wface marco',
			'@wface period 0.2',
			'face position 200,200,300,200,200,300,400,200,300,500,800,100,100,300',
			'face position 200,200,200,200,200,300,200,200,100,300,300,300,100,200',
			'face position 300,100,300,200,100,200,400,200,200,200,500,200,200,100',
			'face position 200,200,200,200,200,300,200,200,100,300,300,300,100,200',
			'@wface stop'
		]
		return Script(script)

if __name__ == '__main__': main()