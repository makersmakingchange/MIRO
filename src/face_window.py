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
	global activation_hist
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
		
	thresh = last_face_pts.vel_sum / 8 + 15
	m_thresh = last_face_pts.vel_sum / 8 + 15
	
	activated = False
	m_act = False
	
	if last_face_pts.vels[0].y > thresh and last_face_pts.vels[1].y > thresh:
		if last_face_pts.vels[0].length() > last_face_pts.vel_sum / 7 and  last_face_pts.vels[1].length() > last_face_pts.vel_sum / 7:
			activated = True
	if last_face_pts.vels[5].y - last_face_pts.vels[6].y > thresh:
		if last_face_pts.vels[0].length() > last_face_pts.vel_sum / 7 and  last_face_pts.vels[1].length() > last_face_pts.vel_sum / 7:
			m_act = True
	
	if activation_hist[0][0] == False and activation_hist[1][0] == False and activation_hist[2][0] == False and activation_hist[3][0] == False and activated == True:
		push.send_string('@engine sel=0')
	else:
		activated = False
	
	if activation_hist[0][1] == False and activation_hist[1][1] == False and activation_hist[2][1] == False and activation_hist[3][1] == False and m_act == True:
		push.send_string('@engine sel=1')
	else:
		m_act = False

	activation_hist[3] = list(activation_hist[2])
	activation_hist[2] = list(activation_hist[1])
	activation_hist[1] = list(activation_hist[0])
	activation_hist[0][0] = activated
	activation_hist[0][1] = m_act

	write('vel sum '+str(face_pts.vel_sum)
		+'\nl_brow '+str(face_pts.vels[1].length())
		+'\nraised '+str(activation_hist))

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
				interpreter[parts[0]](parts[1])
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
console_font = font.Font(family='Helvetica',size=12,weight='bold')
point_font = font.Font(family='Helvetica',size=8,weight='bold')

last_face_pts = None
activation_hist = [[False,False],[False,False],[False,False],[False,False]]
interpreter = {}
interpreter['cmd'] = command
interpreter['write'] = write
interpreter['face'] = process_face_coords

history = []
t_hist = []
activated = [False,False]

gui = Application(master=root,size=(640,480))
gui.mainloop()
gui.quit()