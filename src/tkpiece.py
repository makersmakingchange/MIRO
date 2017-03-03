from wtfj import *
from Tkinter import *
import tkFont as font
import time
import math

IMAGE_PATH = '../img/'

import logging
logging.basicConfig(filename='system.log',
	filemode='a',
	format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
	datefmt='%H:%M:%S',
	level=logging.DEBUG)
logger = logging.getLogger('tkpiece')

tkp = None

def ON_mouse(event):
	tkp.send(Msg.MOUSE,str(event.x)+','+str(event.y))

class TkPiece(Piece,Frame):

	def _AFTER_start(self):
		self._root = Tk()
		Frame.__init__(self,self._root)
		self._canvas = Canvas(self._root,width=640,height=480)
		self._canvas.bind("<Motion>",ON_mouse)
		self._canvas.bind_all("<Escape>",self._ON_esc)
		self._canvas.pack()
		self._then = time.clock()
		self._images = {}
		self._fonts = {
			Msg.CONSOLE : font.Font(family='Helvetica',size=36, weight='bold')
		}
		self._handles = {
			Msg.CONSOLE : self._canvas.create_text(320,240,justify='center',font=self._fonts['console'])
		}
		Frame.mainloop(self)

	def _DURING_poll(self): 
		now = time.clock()
		delta = now - self._then
		self.send(Req.PERIOD,str(delta))
		self._then = now

	def _BEFORE_stop(self): Frame.quit(self)

	def _ON_esc(self,data): self.stop()

	def _ON_image(self,data):
		import os
		from PIL import Image, ImageTk
		image = Image.open(IMAGE_PATH+data)
		photo = ImageTk.PhotoImage(image)
		self._images[data] = photo
		handle = self._canvas.create_image(320,240,image=photo)
		self._canvas.tag_lower(handle)
		#self._canvas._create
		self._canvas.pack()
		self.send(Msg.ACK)

	def _ON_font(self,data):
		fontname,size = data.split(',')
		img = self._canvas.itemconfigure(self._handles[fontname],font=('',int(size)))
		self.send(Msg.ACK)

	def _ON_position(self,data):
		fontname,x,y = data.split(',')
		self._canvas.coords(self._handles[Msg.CONSOLE],x,y)

	def _ON_console(self,data):
		self._canvas.itemconfigure(self._handles[Msg.CONSOLE],text=data)

def motion(t):
	f = t**2
	A,B = 0.1,0.2
	x = A*t*math.sin(f/10.0) + 320
	y = B*t*math.sin((f+5)/10.0) + 240
	return (int(x),int(y))

class Wtfj:

	@staticmethod
	def test(): 
		global tkp
		A,c = 10,80
		#int(A*math.sin(x/4.0)) + 
		sizes = [c + x for x in range(200)]

		script = [
			'@tkpiece marco',
			'@tkpiece console WELCOME',
			'@tkpiece period 0.04'
		]
		for fontsize in sizes[:50]:
			msg = '@tkpiece font console,'+str(fontsize)
			script.append(msg)
		script.append('@tkpiece console TO')
		for fontsize in sizes[:50]:
			msg = '@tkpiece font console,'+str(fontsize)
			script.append(msg)
		script.append('@tkpiece console wtfj')
		script.append('@tkpiece font console,300')
		script.append('@tkpiece period 2')
		script.append('@tkpiece period 0.04')
		for t in range(100):
			x,y = motion(t)
			if t == 50:
				script.append('@tkpiece font console,100')
				script.append('@tkpiece image test.jpg')
				script.append('@tkpiece console EXITING')
			else:
				script.append('@tkpiece position console,'+str(x)+','+str(y))	
		script.append('@tkpiece stop')

		image = ['@tkpiece period 2','@tkpiece image test.jpg','system idle','@tkpiece stop']

		tkp = TkPiece(Script(script),Printer('PIECE RECV < ' ))
		tkp.start()

	@staticmethod
	def console():
		global tkp
		tkp = TkPiece(Console('[>] '),Printer('[<]' ))
		tkp.start()

	@staticmethod
	def exe():
		assert False

	@staticmethod
	def zmq():
		global tkp
		# Client connections
		zsub = ZmqSubscriber() # Filters incoming messages to uid 'test'
		zpush = ZmqPusher() # Pushes messages back to server
		tkp = TkPiece(zsub,zpush)
		tkp.start()

if __name__ == '__main__':
	from sys import argv
	run_mode = Mode.TEST
	print('Running with args '+repr(argv))
	
	try:
		run_mode = argv[1]
		msg = pack(Uid.SYSTEM,Msg.MODE,run_mode)
		logger.info(msg)
		print(msg)
		if int(run_mode) & Mode.CONSOLE:
			Wtfj.console()
		if int(run_mode) & Mode.ZMQ:
			Wtfj.zmq()
		else:
			Wtfj.test()
	except (IndexError,AssertionError) as e:
		msg = pack(Uid.SYSTEM,Msg.ERR,'Bad or no args '+repr(argv)+'\n'+repr(e))
		logger.info(msg)
		print(msg)
		msg = pack(Uid.SYSTEM,Msg.MODE,Mode.TEST)
		logger.debug(msg)
		print(msg)
		Wtfj.test()
	except Exception as e:
		logger.error(e)