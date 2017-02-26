# See wtfj/__init__.py for full list of imports
from wtfj import *
from Tkinter import *
import tkFont as font
import time
import copy

# Constants and stable vars
SOCKET_SUB = 'tcp://localhost:5556'
SOCKET_PUSH = 'tcp://localhost:5557'
topic_filter = '@face_window'
interest_filter = 'face'

# Connect to sockets
context = zmq.Context()
push = context.socket(zmq.PUSH)
sub = context.socket(zmq.SUB)
push.connect(SOCKET_PUSH)
sub.connect(SOCKET_SUB)

if isinstance(topic_filter,bytes):
	topic_filter = topic_filter.decode('ascii')
if isinstance(interest_filter,bytes):
	interest_filter = interest_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,topic_filter)
sub.setsockopt_string(zmq.SUBSCRIBE,interest_filter)

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

def command(cmd_string):
	if cmd_string == 'quit':
		quit()

def write(console_text):
	gui.canvas.itemconfigure(gui.console,text=console_text)

def option(option_msg):
	option_msg = option_msg.replace('_to_',':')
	parts = option_msg.split(',')
	gui.canvas.itemconfigure(gui.left,text=parts[0])
	gui.canvas.itemconfigure(gui.right,text=parts[1])

def process_face_coords(data):
	global history
	global t_hist
	global activated
	global last_face_pts

	d = [int(float(coord)) for coord in data.split(',')]
	face_pts = DetectedFace(d)
	face_pts.draw(gui.canvas)
	if last_face_pts is not None:
		face_pts.draw_difference(gui.canvas,last_face_pts)
		face_pts.calc_velocities(last_face_pts)
		face_pts.calc_vel_differentials()
		#face_pts.norm_velocities(100)
		face_pts.draw_velocities(gui.canvas,320,240)
		last_face_pts.erase(gui.canvas)
	last_face_pts = face_pts

	write('vel sum '+str(face_pts.vel_sum)
		+'\nl_brow '+str(face_pts.vels[1].length()))

	#for i in range(len(gui.pt_txt)):
	#	gui.canvas.coords(gui.pt_txt[i],d[2*i],d[(2*i)+1])

def on_mouse_move(event):
	push.send_string('mouse '+str(event.x)+','+str(event.y))

def on_esc(event):
	push.send_string('quitting face_window')
	gui._quit()

def on_0(event):
	push.send_string('@engine sel=0')

def on_1(event):
	push.send_string('@engine sel=1')

last_face_pts = None
function_dict = {}
function_dict['cmd'] = command
function_dict['write'] = write
function_dict['face'] = process_face_coords

class Application(Frame,dict):
	def __init__(self,master=None,size=(1080, 720)):
		# Application housekeeping
		Frame.__init__(self,master)
		self.drawables = []
		self.size = size
		self._createWidgets()
		push.send_string('started face_window')

	def _createWidgets(self):
		''' Create the base canvas, menu/selection elements, mouse/key functions '''
		self.canvas = Canvas(self.master,width=self.size[0],height=self.size[1])
		w,h = self.size[0],self.size[1]

		#self.drawables.append(Box(0,0,w/3,h,fill=make_color(255,0,0)))
		#self.drawables.append(Box(2*w/3,0,w,h,fill=make_color(255,0,0)))

		# Initial drawing of all Drawables
		for drawable in self.drawables:
			drawable.draw(self.canvas)

		self.console = self.canvas.create_text(0,0,anchor='nw',font=console_font)
		self.brow_eye_r = self.canvas.create_line(0,0,0,0,width=3.0)
		self.brow_eye_l = self.canvas.create_line(0,0,0,0,width=3.0)
		self.mouthline = self.canvas.create_line(0,0,0,0,width=3.0,fill='blue')

		self.canvas.bind("<Motion>",on_mouse_move)
		self.canvas.bind_all("<Escape>",on_esc)
		self.canvas.bind_all("0",on_0)
		self.canvas.bind_all("1",on_1)
		self.canvas.pack()

	def _draw_periodic(self):
		try:
			parts = sub.recv_string(zmq.DONTWAIT).split()
			try:
				function_dict[parts[0]](parts[1])
			except KeyError:
				pass
			except IndexError:
				pass
		except zmq.Again:
			pass

		# Call this loop again after some milliseconds
		self.canvas.after(10,self._draw_periodic)

	def _quit(self):
		Frame.quit(self)

	def mainloop(self):
		go = Thread(target=self._draw_periodic)
		go.start()
		Frame.mainloop(self)
		go.join()

root = Tk()
#root.attributes("-fullscreen", True)
w,h = (root.winfo_screenwidth(),root.winfo_screenheight())
console_font = font.Font(family='Helvetica',size=20,weight='bold')
point_font = font.Font(family='Helvetica',size=8,weight='bold')

history = []
t_hist = []
activated = [False,False]

gui = Application(master=root,size=(640,480))
gui.mainloop()
gui.quit()