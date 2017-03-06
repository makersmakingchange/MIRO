# See wtfj/__init__.py for full list of imports
from wtfj import *
from Tkinter import *
import tkFont as font

# Constants and stable vars
SOCKET_SUB = 'tcp://localhost:5556'
SOCKET_PUSH = 'tcp://localhost:5557'
topic_filter = '@gui'

# Connect to sockets
context = zmq.Context()
push = context.socket(zmq.PUSH)
sub = context.socket(zmq.SUB)
push.connect(SOCKET_PUSH)
sub.connect(SOCKET_SUB)

if isinstance(topic_filter,bytes):
	topic_filter = topic_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,topic_filter)

def command(cmd_string):
	if cmd_string == 'quit':
		quit()

def region_cmd(region_string):
	if region_string == 'get':
		push.send_string('gui regions '+ gui.shape_list)

def write(console_text):
	if (console_text == 'spc'):
		gui.selected_text += ' '
	else:
		if (console_text != '#empty'):
			gui.selected_text += console_text
	gui.canvas.itemconfigure(gui.text_display,text=gui.selected_text)

def option(option_msg):
	option_msg = option_msg.replace('_to_',':')
	parts = option_msg.split(',')
	for i in range(len(parts)):
		if (parts[i] == "#empty"):
			gui.canvas.itemconfigure(gui.text_boxes[i],text='')
		else:	
			gui.canvas.itemconfigure(gui.text_boxes[i],text=parts[i])

function_dict = {}
function_dict['cmd'] = command
function_dict['write'] = write
function_dict['opt'] = option
function_dict['regions'] = region_cmd

def on_mouse_move(event):
	push.send_string('mouse '+str(event.x)+','+str(event.y))

def on_esc(event):
	push.send_string('gui exiting')
	gui._quit()

def on_0(event):
	push.send_string('@engine sel=0')

def on_1(event):
	push.send_string('@engine sel=1')

class Application(Frame):
	def __init__(self,master=None,size=None):
		# Application housekeeping
		Frame.__init__(self,master)
		self.drawables = []
		self.size = size
		self._divide_screen(5)
		self._createWidgets()
		self.selected_text = ''

	def _divide_screen(self,n):
		max_rows = 5
		shape_type = 'rect'
		screen_width = self.size[0]
		screen_height = self.size[1]
		assert(max_rows == 5)
		if (n > max_rows):
			cols = n/max_rows + (n%max_rows > 0)
		elif(n == max_rows):
			cols = n/(max_rows/2) + (n%(max_rows/2) > 0) - 1
		else:
			cols = n/2 + (n%2 > 0)
		col_keys = []
		for x in range(cols):
			col_keys.append(1)

		i = 0
		while(sum(col_keys) != n):
			col_keys[i%len(col_keys)] += 1
			i+=1

		self.shape_list = ""
		dx = screen_width / (len(col_keys))

		i = 0
		for val in reversed(col_keys):
			dy = screen_height / (val)
			j = 1
			for x in range(0,val):
				ul = (i*dx,x*dy)
				br = (min(screen_width,(i+1)*dx),min(screen_height,(x+1)*dy))
				self.shape_list = self.shape_list + shape_type + "," + str(ul[0]) + "," + str(ul[1]) + "," + str(br[0]) + "," + str(br[1]) + ","
				j+=1

			i+=1
		self.shape_list = self.shape_list[0:len(self.shape_list)-1]



	def _draw_text(self):
		for x in range(len(self.shapes)):
			shape_center = ((self.br_coords[x][0]-self.ul_coords[x][0])/2 + self.ul_coords[x][0],(self.br_coords[x][1]-self.ul_coords[x][1])/2 + self.ul_coords[x][1])
			self.text_boxes.append(self.canvas.create_text(shape_center[0],shape_center[1],justify='center',font=console_font))

	def _draw_shapes(self):
		self.text_boxes = []
		for x in range(len(self.shapes)):
			self.drawables.append(Box(self.ul_coords[x][0],self.ul_coords[x][1],self.br_coords[x][0],self.br_coords[x][1],fill=make_color(255,0,0)))
			
	def _build_screen(self):
		items = self.shape_list.split(",")
		for i in range(len(items)):
			if (i%5 == 0):
				self.shapes.append(items[i])
				self.ul_coords.append((int(items[i+1]),int(items[i+2])))
				self.br_coords.append((int(items[i+3]),int(items[i+4])))
		self._draw_shapes()

	def _createWidgets(self):
		''' Create the base canvas, menu/selection elements, mouse/key functions '''
		self.canvas = Canvas(self.master,width=self.size[0],height=self.size[1])
		w,h = self.size[0],self.size[1]

		self.ul_coords = []
		self.br_coords = []
		self.shapes = []

		self._build_screen()
		# Initial drawing of all Drawables
		for drawable in self.drawables:
			drawable.draw(self.canvas)

		self._draw_text()

		self.text_display = self.canvas.create_text(0,h-150,justify='left',font=text_display_font)
		self.canvas.itemconfigure(self.text_display, anchor='w')

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
					except IndexError:
						pass
		except zmq.Again:
			pass

		# Call this loop again after some milliseconds
		self.canvas.after(10, self._draw_periodic)

	def _quit(self):
		Frame.quit(self)

	def mainloop(self):
		go = Thread(target=self._draw_periodic)
		go.start()
		Frame.mainloop(self)
		go.join()


root = Tk()
root.attributes("-fullscreen", True)
w,h = (root.winfo_screenwidth(),root.winfo_screenheight())
console_font = font.Font(family='Helvetica',size=300, weight='bold')
text_display_font = font.Font(family='Helvetica',size=50, weight='bold')
gui = Application(master=root,size=(w,h))
gui.mainloop()
gui.quit()