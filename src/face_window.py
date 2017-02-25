# See wtfj/__init__.py for full list of imports
from wtfj import *
from Tkinter import *
import tkFont as font

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
	d = [int(coord) for coord in d]
	p = ((d[0]+d[2])/2,(d[1]+d[3])/2) #nose_point

	brow_length = 	  ((d[0]-d[2])**2 + (d[1]-d[3])**2)**0.5
	noseline_length = ((p[0]-d[4])**2 + (p[1]-d[5])**2)**0.5
	mouth_length = 	  ((d[6]-d[8])**2 + (d[7]-d[9])**2)**0.5

	ratio = noseline_length/brow_length
	history.append(ratio)
	t_hist.append(time.clock())
	if len(history) == 10:
		history = history[1:len(history)]
		t_hist = t_hist[1:len(t_hist)]

		metric = (sum(history[5:9]))/4 - sum(history)/9
		
		if metric > 0.03:
			if activated[0] == False:
				activated[0] = True
				push.send_string('@engine sel=0')
		else:
			activated[0] = False

		if mouth_length > 20:
			if activated[1] == False:
				activated[1] = True
				push.send_string('@engine sel=1')
		else:
			activated[1] = False
		

		write('nose_length '+str(noseline_length)+'\n'
			+'mouth_length '+str(mouth_length)+'\n'
			+'metric'+str(int(metric*1000)))

	gui.canvas.coords(gui.eyebrow,  d[0],d[1],d[2],d[3])
	gui.canvas.coords(gui.noseline, p[0],p[1],d[4],d[5])
	gui.canvas.coords(gui.mouthline,d[8],d[9],d[6],d[7])

function_dict = {}
function_dict['cmd'] = command
function_dict['write'] = write
function_dict['face'] = process_face_coords

def on_mouse_move(event):
	push.send_string('mouse '+str(event.x)+','+str(event.y))

def on_esc(event):
	push.send_string('gui exiting')
	gui.quit()

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
		self.eyebrow = self.canvas.create_line(0,0,0,0,width=3.0)
		self.noseline = self.canvas.create_line(0,0,0,0,width=3.0)
		self.mouthline = self.canvas.create_line(0,0,0,0,width=3.0,fill='blue')

		self.canvas.bind("<Motion>",on_mouse_move)
		self.canvas.bind_all("<Escape>",on_esc)
		self.canvas.bind_all("0",on_0)
		self.canvas.bind_all("1",on_1)
		self.canvas.pack()

	def _draw_periodic(self):
		try:
			parts = sub.recv_string(zmq.DONTWAIT).split()
			if len(parts) > 0:
				msg_parts = parts[1].split('=')
				if len(msg_parts) > 0:
					try:
						function_dict[msg_parts[0]](msg_parts[1])
					except KeyError:
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

history = []
t_hist = []
activated = [False,False]

gui = Application(master=root,size=(640,480))
gui.mainloop()
gui.quit()