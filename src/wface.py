from wtfj import *
from tkpiece import TkPiece

def main():
	from sys import argv
	Runner.run_w_cmd_args(WFace,argv,[Uid.FACE])


def distance(x1,y1,x2,y2):
	((x1-x2)**2 + (y1-y2)**2)**0.5

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


class WFace(TkPiece):
	def _ON_draw(self,data):
		self._face_handles = ['rb','lb','re','le','n','um','lm']
		for handle in self._face_handles:
			self._ON_create(pack_csv(Msg.TEXT,handle,0.5,0.5))
			self._ON_text(handle+','+handle)
		self.send(Msg.ACK)

	def _ON_face_position(self,data):
		vals = [float(n) for n in data.split(',')]
		for i in range(len(vals)/2):
			x,y = vals[2*i]/640,vals[(2*i)+1]/480
			self._ON_position(pack_csv(self._face_handles[i],x,y))
		self.send(Msg.ACK)

	@staticmethod
	def script():
		script = [
			'@wface marco',
			'@wface period 1',
			'@wface draw',
			'@wface text feedback,TESTING WFACE',
			'face position 1.12131,1231,121,258,433,456,4566,200',
			'@wface stop'
		]
		return Script(script)

if __name__ == '__main__': main()