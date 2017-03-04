from wtfj import *
from Tkinter import *
import tkFont as font
import time
import math

IMAGE_PATH = '../img/'

def main():
	from sys import argv
	Runner.run_w_cmd_args(TkPiece,argv)

class TkPiece(Piece,Frame):

	tkpiece_ref = None # Needed for events like ON_mouse

	def _AFTER_start(self):
		self._root = Tk()
		TkPiece.tkpiece_ref = self
		Frame.__init__(self,self._root)
		self._canvas = Canvas(self._root,width=1080,height=720)
		self._canvas.bind("<Motion>",TkPiece.ON_mouse)
		self._canvas.bind_all("<Escape>",self._ON_esc)
		self._canvas.pack()
		self._then = time.clock()
		self._images = {}
		self._fonts = {
			Msg.CONSOLE : font.Font(family='Helvetica',size=36, weight='bold')
		}
		self._handles = {
			Msg.CONSOLE : self._canvas.create_text(540,360,justify='center',font=self._fonts['console'])
		}
		Frame.mainloop(self)

	def _DURING_poll(self): 
		now = time.clock()
		delta = now - self._then
		self._then = now

	def _BEFORE_stop(self): # Tk window requires a custom start routine
		self._alive = False
		Frame.quit(self)

	def _ON_esc(self,data): self.stop()

	def _ON_image(self,data):
		import os
		from PIL import Image, ImageTk
		image = Image.open(IMAGE_PATH+data)
		photo = ImageTk.PhotoImage(image)
		self._images[data] = photo
		handle = self._canvas.create_image(540,360,image=photo)
		self._canvas.tag_lower(handle)
		#self._canvas._create
		self._canvas.pack()
		self.send(Msg.ACK)

	def _ON_font(self,data):
		fontname,size = data.split(',')
		img = self._canvas.itemconfigure(self._handles[fontname],font=('',int(size)))
		self.send(Msg.ACK)

	def _ON_position(self,data):
		try:
			fontname,x,y = data.split(',')
			self._canvas.coords(self._handles[Msg.CONSOLE],int(x),int(y))
		except ValueError as e:
			self.err('Position ['+str(data)+'] not valid\n'+repr(e))

	def _ON_console(self,data):
		try:
			self._canvas.itemconfigure(self._handles[Msg.CONSOLE],text=data)
		except Exception(e):
			self.err('Function called before canbas initialized\n'+repr(e))

	@staticmethod
	def ON_mouse(event):
		try:
			TkPiece.tkpiece_ref.send(Msg.MOUSE,str(event.x)+','+str(event.y))
			TkPiece.tkpiece_ref._interpret('@tkpiece position console,'+str(event.x)+','+str(event.y))
		except Exception as e:
			with open('tkerr.txt','w') as f: f.write(repr(e))

	@staticmethod
	def script():
		A,c = 10,80
		sizes = [c + x for x in range(200)]

		def motion(t):
			f = t**1.6
			A,B = 0.1,0.2
			x = A*t*math.sin(f/10.0) + 540
			y = B*t*math.sin((1.1*f+5)/10.0) + 360
			return (int(x),int(y))

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
		for t in range(150):
			x,y = motion(t)
			if t == 25: script.append('@tkpiece image test.jpg')
			if t == 50:
				script.append('@tkpiece period 0.001')
				script.append('@tkpiece console  ')
				script.append('@tkpiece font console,100')
				script.append('@tkpiece image test.jpg')
				script.append('@tkpiece console EXITING')
				script.append('@tkpiece period 0.004')
			else:
				script.append('@tkpiece position console,'+str(x)+','+str(y))	
		script.append('@tkpiece stop')

		return Script(script)


if __name__ == '__main__': main()