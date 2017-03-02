from wtfj import *
from Tkinter import *
import tkFont as font
import time


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
		self._fonts = {
			Msg.CONSOLE : font.Font(family='Helvetica',size=36, weight='bold')
		}
		self._text = {
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

	def _ON_console(self,data):
		self._canvas.itemconfigure(self._text[Msg.CONSOLE],text=data)

try:
	raw_input()
	incoming = Console('[>] ')
except EOFError as e: # No console input available
	incoming = Script([
		'@tkpiece marco',
		'@tkpiece period 0.2'
	])
outgoing = Printer('[<] ')
tkp = TkPiece(incoming,outgoing)
tkp.start()
tkp.stop()