# For future compatibility with python 3
from __future__ import print_function
from __future__ import unicode_literals
# Python imports
import sys
from threading import Thread
# Dynamic import of tk if python 2 or 3
try:
	assert sys.version_info[0] == 3
	from tkinter import *
	import tkinter.font as font
except AssertionError as e:
	from Tkinter import *
	import tkFont as font
# Third-party imports
import zmq

# Constants and stable vars
SOCKET_SUB = 'tcp://localhost:5556'
SOCKET_PUSH = 'tcp://localhost:5557'
topic_filter = 'gui'

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

def write(console_text):
	gui.canvas.itemconfigure(gui.console,text=console_text)

function_dict = {}
function_dict['cmd'] = command
function_dict['write'] = write

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
		self.console = self.canvas.create_text(100,100,font=console_font)
		self.canvas.pack()

	def _draw_periodic(self):
		try:
			string = sub.recv_string(zmq.DONTWAIT)
			parts = string.split()
			if len(parts) > 0:
				msg_parts = parts[1].split('=')
				if len(msg_parts) > 0:
					try:
						function_dict[msg_parts[0]](msg_parts[1])
					except KeyError:
						pass
		except zmq.Again:
			pass
		for drawable in self.drawables:
			drawable.update(self.canvas,input_device)
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
#root.attributes("-fullscreen", True)
w,h = (root.winfo_screenwidth(),root.winfo_screenheight())
console_font = font.Font(family='Helvetica',size=50, weight='bold')

gui = Application(master=root,size=(500,500))
gui.mainloop()
gui.quit()