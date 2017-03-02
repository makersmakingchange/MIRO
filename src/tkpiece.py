from wtfj import *
from Tkinter import *
import tkFont as font
import time

class TkPiece(Piece,Frame):

	def _AFTER_start(self):
		self._root = Tk()
		Frame.__init__(self,self._root)
		Frame.mainloop(self)

	def _DURING_poll(self): pass

	def _BEFORE_stop(self): pass

try:
	raw_input()
	incoming = Console('[>] ')
	outgoing = Printer('[<] ')
except EOFError as e: # No console input available
	incoming = Script(['@tkpiece marco'])
	outgoing = Printer('[<] ')

	tkp = TkPiece(incoming,outgoing)
	tkp.start()
	
tkp.stop()