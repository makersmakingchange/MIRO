# See wtfj/__init__.py for full list of imports
from wtfj import *
from Tkinter import *
import tkFont as font
import time

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
	global history
	global t_hist
	global activated

	d = data.split(',')
	d = [int(float(coord)) for coord in d]

	for i in range(len(gui.points)):
		gui.canvas.coords(gui.points[i],d[2*i],d[(2*i)+1])

	['br','bl','er','el','n','mu','ml']

	brow_eye_r = 	((d[0] -d[4])**2  + (d[1] -d[5])**2)**0.5
	brow_eye_l = 	((d[2] -d[6])**2  + (d[3] -d[7])**2)**0.5
	mouth_length =	((d[10]-d[12])**2 + (d[11]-d[13])**2)**0.5

	write('brow_eye_r '+str(brow_eye_r)+'\n'
		+'brow_eye_l '+str(brow_eye_l)+'\n'
		+'mouth_length '+str(mouth_length))

	gui.canvas.coords(gui.brow_eye_r,d[0], d[1], d[4], d[5])
	gui.canvas.coords(gui.brow_eye_l,d[2], d[3], d[6], d[7])
	gui.canvas.coords(gui.mouthline, d[10],d[11],d[12],d[13])

function_dict = {}
function_dict['cmd'] = command
function_dict['write'] = write
function_dict['face'] = process_face_coords

def on_mouse_move(event):
	push.send_string('mouse '+str(event.x)+','+str(event.y))

def on_esc(event):
	push.send_string('quitting face_window')
	gui._quit()

def on_0(event):
	push.send_string('@engine sel=0')

def on_1(event):
	push.send_string('@engine sel=1')

class Application(Frame):
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

		points = ['br','bl','er','el','n','mu','ml']
		self.points = [self.canvas.create_text(0,0,font=point_font,text=p) for p in points]

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