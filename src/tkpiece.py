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
		self._w = 1080 
		self._h = 720
		self._canvas = Canvas(self._root,width=self._w,height=self._h)
		self._canvas.bind("<Motion>",TkPiece.ON_mouse)
		self._canvas.bind_all("<Escape>",self._ON_esc)
		self._canvas.pack()
		self._then = time.clock()
		self._images = {}
		self._fonts = {
			'default' : font.Font(family='Helvetica',size=72, weight='bold'),
			'feedback' : font.Font(family='Helvetica',size=36, weight='bold')
		}
		self._handles = {
			'feedback' : self._canvas.create_text(self._w/2,self._h/2,justify='center',font=self._fonts['feedback'])
		}
		Frame.mainloop(self)

	def _BEFORE_stop(self): # Tk window requires a custom start routine
		self._alive = False
		Frame.quit(self)

	def _ON_esc(self,data): self.stop()

	def _ON_image(self,data):
		import os
		from PIL import Image,ImageTk
		image_file,x,y = data.split(',')
		#TODO This is a lazy and stupid way to load images
		try:
			image = Image.open(IMAGE_PATH+image_file+'.png')
		except IOError:
			image = Image.open(IMAGE_PATH+image_file+'.jpg')
		photo = ImageTk.PhotoImage(image)
		self._images[image_file] = photo
		x = int(self._w*float(x))
		y = int(self._h*float(y))
		handle = self._handles[image_file] = self._canvas.create_image(x,y,image=photo)
		self._canvas.tag_lower(handle)
		self._canvas.pack()
		self.send(Msg.ACK)

	def _ON_fontsize(self,data):
		parts = data.split(',')
		font_handles = parts[:-1]
		size = parts[-1]
		for font_handle in font_handles:
			self._canvas.itemconfigure(self._handles[font_handle],font=('',int(size)))
		self.send(Msg.ACK)

	def _ON_position(self,data):
		try:
			handle,x,y = data.split(',')
			self._canvas.coords(self._handles[handle],int(x),int(y))
		except ValueError as e:
			self.err('Position ['+str(data)+'] not valid\n'+repr(e))

	def _ON_create(self,data):
		item,handle,x,y = data.split(',')
		x = int(float(x) * self._w)
		y = int(float(y) * self._h)
		if item == 'text':
			try:
				item_font = self._fonts[handle]
			except KeyError:
				self.err('No font specified for ['+handle+'], using default')
				item_font = self._fonts['default']
			self._handles[handle] = self._canvas.create_text(x,y,justify='center',font=item_font)
			self.send(Msg.ACK)

	def _ON_delete(self,data):
		handles = data.split(',')
		for handle in handles:
			self._canvas.delete(self._handles[handle])

	def _ON_clear(self,data):
		for handle in self._handles:
			self._canvas.delete(self._handles[handle])

	def _ON_text(self,data):
		handle,text = data.split(',')
		try:
			self._canvas.itemconfigure(self._handles[handle],text=text)
			self.send(Msg.ACK)
		except Exception as e:
			self.err('Function called before canvas initialized')
			raise e

	@staticmethod
	def ON_mouse(event):
		try:
			TkPiece.tkpiece_ref.send(Msg.MOUSE,str(event.x)+','+str(event.y))
			#TkPiece.tkpiece_ref._interpret('@tkpiece position feedback,'+str(event.x)+','+str(event.y))
		except Exception as e:
			with open('tkerr.txt','w') as f: f.write(repr(e))

	@staticmethod
	def script():

		text_entry = [
			'@tkpiece marco',
			'@tkpiece create text,key0,0.25,0.25',
			'@tkpiece create text,key1,0.25,0.75',
			'@tkpiece create text,key2,0.75,0.25',
			'@tkpiece create text,key3,0.75,0.75',
			'@tkpiece fontsize key0,key1,key2,key3,150',
			'@tkpiece period 1',
			'@tkpiece text key0,M',
			'@tkpiece text key1,I',
			'@tkpiece text key2,R',
			'@tkpiece text key3,O',
			'@tkpiece period 0.5',
			'@tkpiece text key0,m',
			'@tkpiece text key1,i',
			'@tkpiece text key2,r',
			'@tkpiece text key3,o',
			'@tkpiece delete key0,key1',
			'@tkpiece delete key2',
			'@tkpiece delete key3',
			'@tkpiece text feedback,That\'s all folks',
			'@tkpiece clear',
			'@tkpiece period 1',
			'@tkpiece image test,0.5,0.5',
			'@tkpiece create text,exit_msg,0.5,0.5',
			'@tkpiece text exit_msg,NOT',
			'@tkpiece stop'
		]

		return Script(text_entry)


if __name__ == '__main__': main()

#root = Tk()
#root.attributes("-fullscreen", True)
#w,h = (root.winfo_screenwidth(),root.winfo_screenheight())