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
		self._canvas = Canvas(self._root,width=200,height=200)
		self._canvas.bind("<Motion>",ON_mouse)
		self._canvas.bind_all("<Escape>",self._ON_esc)
		self._canvas.pack()
		self._then = time.clock()
		Frame.mainloop(self)

	def _DURING_poll(self): 
		now = time.clock()
		delta = now - self._then
		self.send(Req.PERIOD,str(delta))
		self._then = now

	def _BEFORE_stop(self): Frame.quit(self)

	def _ON_esc(self,data): self.stop()


try:
	raw_input()
	incoming = Console('[>] ')
	outgoing = Printer('[<] ')
except EOFError as e: # No console input available
	
	incoming = Script([
		'@tkpiece marco',
		'@tkpiece period 0.2'
	])
	outgoing = Printer('[<] ')

tkp = TkPiece(incoming,outgoing)
tkp.start()