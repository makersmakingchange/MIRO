from wtfj import *
from Tkinter import *
import tkFont as font
import time
import math
import os
from PIL import Image,ImageTk

IMAGE_PATH = '../img/'

def main():
	from sys import argv
	Runner.run_w_cmd_args(TkPiece,argv)

class TkPiece(Piece,Frame):

	tkpiece_ref = None # Needed for events like ON_mouse

	def scale(self,x,y):
		return float(x)/self._w,float(y)/self._h

	def _AFTER_start(self):
		self._root = Tk()
		TkPiece.tkpiece_ref = self
		Frame.__init__(self,self._root)
		self._root.attributes("-fullscreen", True)
		self._w,self._h = (self._root.winfo_screenwidth(),self._root.winfo_screenheight()) 
		self._canvas = Canvas(self._root,width=self._w,height=self._h)
		self._canvas.bind("<Motion>",TkPiece.on_mouse_move)
		self._canvas.bind("<ButtonPress-1>",TkPiece.on_left_click)
		self._canvas.bind("<ButtonPress-3>",TkPiece.on_right_click)
		self._canvas.bind_all("<Escape>",self._ON_esc)
		self._canvas.pack()
		self._then = time.clock()
		self._images = {}
		self._text_size = 200
		self._select_fb_color = 'yellow';
		self._fonts = {
			'default' : font.Font(family='Helvetica',size=self._text_size, weight='bold'),
			'feedback' : font.Font(family='Helvetica',size=self._text_size, weight='bold')
		}
		self._handles = {
			'feedback' : self._canvas.create_text(self._w-(self._text_size/2),self._h - (self._text_size/1.5),justify='right',font=self._fonts['feedback'])
		}
		self._canvas.itemconfigure(self._handles['feedback'],anchor='e')
		self._translation_table = {
			'num': '#',
			'com': ','
		}
		Frame.mainloop(self)
		'''Translation table must be updated in both tkpiece and text'''

	def _BEFORE_stop(self): # Tk window requires a custom start routine
		self._alive = False
		Frame.quit(self)

	def _interpret(self,msg):
		try:
			Piece._interpret(self,msg)
		except TclError as e:
			self.err('Graphics error\n'+repr(e))

	def _ON_esc(self,data):
                self.send_to(Uid.SYSTEM,Req.STOP)
                self.stop()

	def _ON_image(self,data):
		try:
			
			image_file,x,y,w,h = data.split(',')

			w = int(float(w)*self._w)
			h = int(float(h)*self._h)

			#TODO This is a lazy and stupid way to load images
			try:
				image = Image.open(IMAGE_PATH+image_file+'.png')
			except IOError:
				image = Image.open(IMAGE_PATH+image_file+'.jpg')
			image = image.resize((h,h), Image.ANTIALIAS)
			photo = ImageTk.PhotoImage(image)
			self._images[image_file] = photo
			x = int(self._w*float(x))
			y = int(self._h*float(y))
			handle = self._handles[image_file] = self._canvas.create_image(x,y,image=photo)
			self._canvas.pack()
		except TclError as e:
			self.err('Graphics error\n'+repr(e))

	def _ON_to_background(self,data):
		# TODO make this work
		handle = data
		self._canvas.tag_lower(handle)

	def _ON_fontsize(self,data):
		'''Resize font of all on-screen text'''
		parts = data.split(',')
		font_handles = parts[:-1]
		size = int(float(parts[-1])*self._w/4.5)
		if (size != self._text_size):
			self._fonts['default'] = font.Font(family='Helvetica',size=size, weight='bold')
			self._text_size = size
			for font_handle in self._handles:
				try:
					self._canvas.itemconfigure(self._handles[font_handle],font=font.Font(family='Helvetica',size=size,weight='bold'))
				except TclError:
					# pass on items that don't have font value (shapes)
					pass

	def _ON_position(self,data):
		try:
			parts = data.split(',')
			if len(parts) == 3:
				handle,x,y = parts
				x = int(self._w*float(x))
				y = int(self._h*float(y))
				self._canvas.coords(self._handles[handle],x,y)
			elif len(parts) == 4:
				handle,x,y,r = parts
				r = int(r)
				x = int(self._w*float(x))
				y = int(self._h*float(y))
				self._canvas.coords(self._handles[handle],x-r,y-r,x+r,y+r)
		except ValueError as e:
			self.err('Position ['+str(data)+'] not valid\n'+repr(e))
		except TclError as e:
			self.err('Graphics error\n'+repr(e))

	def _ON_create(self,data):
		try:
			parts = data.split(',')
			item = parts[0]
			handle = parts[1] 
			x,y = parts[2],parts[3]
			x = int(float(x)*self._w)
			y = int(float(y)*self._h)
			if item == 'text':	
				try:
					item_font = self._fonts[handle]
				except KeyError:
					self.err('No font specified for ['+handle+'], using default')
					item_font = self._fonts['default']
				self._handles[handle] = self._canvas.create_text(x,y,justify='center',font=item_font)
			elif item == 'circle':
				r = int(parts[4])
				color = parts[5]
				self._handles[handle] = self._canvas.create_oval(x-r,y-r,x+r,y+r,fill=color,outline=color)
		except TclError as e:
			self.err('Graphics error\n'+repr(e))

	def _ON_feedback(self,data):
		parts = data.split(',')
		try:
			self._canvas.delete(self._handles['selection_feedback'])
		except KeyError:
			pass
		self._handles['selection_feedback'] = self._canvas.create_rectangle(float(parts[0])*self._w,float(parts[1])*self._h,float(parts[2])*self._w,float(parts[3])*self._h,fill=self._select_fb_color,outline='black')
		self._canvas.tag_lower(self._handles['selection_feedback'])


	def _ON_delete(self,data):
		try:
			handles = data.split(',')
			for handle in handles:
				self._canvas.delete(self._handles[handle])
		except TclError as e:
			self.err('Graphics error\n'+repr(e))

	def _ON_clear(self,data):
		try:
			for handle in self._handles:
				self._canvas.delete(self._handles[handle])
		except TclError as e:
			self.err('Graphics error\n'+repr(e))

	def _translate(self,symbol):
		'''Translates special character to what needs to be displayed''' 
		translation = symbol
		try:
			translation = self._translation_table[symbol]
		except KeyError:
			pass
		return translation

	def _ON_text(self,data):
		parts = data.split(',')
		for x in range(len(parts)):
			parts[x] = self._translate(parts[x])
		handle = parts[0]
		text = ''
		if len(parts) > 2:
			for part in parts[1:]:
				text += (part + ',')
			text = text[:-1]
		else:
			text = parts[1]
		try:
			self._canvas.itemconfigure(self._handles[handle],text=text)
		except TclError as e:
			self.err('Graphics error\n'+repr(e))

	def _ON_changecolor(self,data):
		# data in format: text,background,preselect
		parts = data.split(',')
		self._canvas.configure(background=parts[1])
		self._select_fb_color = parts[2]

	@staticmethod
	def on_mouse_move(event):
		try:
			float_x,float_y = TkPiece.tkpiece_ref.scale(event.x,event.y)
			TkPiece.tkpiece_ref.send(Msg.MOUSE,str(float_x)+','+str(float_y))
		except Exception as e:
			#TkPiece.tkpiece_ref.err(repr(e))
			pass # TODO improve robustness
		except TclError as e:
			#TkPiece.tkpiece_ref.err(repr(e))
			pass # TODO improve robustness

	@staticmethod
	def on_left_click(event):
		try:
			TkPiece.tkpiece_ref.send(Msg.MOUSE,'left_click')
		except Exception as e:
			#TkPiece.tkpiece_ref.err(repr(e))
			pass # TODO improve robustness
		except TclError as e:
			#TkPiece.tkpiece_ref.err(repr(e))
			pass # TODO improve robustness

	@staticmethod
	def on_right_click(event):
		try:
			TkPiece.tkpiece_ref.send(Msg.MOUSE,'right_click')
		except Exception as e:
			#TkPiece.tkpiece_ref.err(repr(e))
			pass # TODO improve robustness
		except TclError as e:
			#TkPiece.tkpiece_ref.err(repr(e))
			pass # TODO improve robustness

	@staticmethod
	def script():
		'''text_entry = [
			'@tkpiece marco',
			'@tkpiece wait 1',
			'@tkpiece create text,key0,0.25,0.25',
			'@tkpiece create text,key1,0.25,0.75',
			'@tkpiece create text,key2,0.75,0.25',
			'@tkpiece create text,key3,0.75,0.75',
			'@tkpiece fontsize key0,key1,key2,key3,150',
			'@tkpiece create circle,cursor,0.5,0.5,50,blue',
			'@tkpiece to_background cursor',
			'@tkpiece to_background cursor',
			'@tkpiece to_background cursor',
			'@tkpiece to_background cursor',
			'@tkpiece to_background cursor',
			'@tkpiece to_background cursor',
			'@tkpiece period 0.5',
			'@tkpiece text key0,M',
			'@tkpiece text key1,I',
			'@tkpiece text key2,R',
			'@tkpiece text key3,O',
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
			'@tkpiece to_background test',
			'@tkpiece create text,exit_msg,0.5,0.5',
			'@tkpiece text exit_msg,NOT',
			'@tkpiece stop'
		]'''
		text_entry = [
			'@tkpiece marco',
			'@tkpiece wait 1',
			'@tkpiece create text,key0,0.25,0.25',
			'@tkpiece create text,key1,0.25,0.75',
			'@tkpiece create text,key2,0.75,0.25',
			'@tkpiece create text,key3,0.75,0.75',
			'@tkpiece period 0.5',
			'@tkpiece text key0,M',
			'@tkpiece feedback 0,0,1,1',
			'@tkpiece text key1,I',
			'@tkpiece text key2,R',
			'@tkpiece text key3,O',
			'@tkpiece fontsize key0,.85',
			'@tkpiece text key0,m',
			'@tkpiece feedback .5,.5,.75,.75',
			'@tkpiece text key1,i',
			'@tkpiece text key2,r',
			'@tkpiece text key3,o',
			'@tkpiece image test,0.5,0.5,1,1',
			'@tkpiece stop'
		]
		return Script(text_entry)


if __name__ == '__main__': main()
