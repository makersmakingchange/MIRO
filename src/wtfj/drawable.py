def make_color(r_uint8,g_uint8,b_uint8):
	''' Color in 24-bit RGB format to '0x#######' string format '''
	r = '0x{:02x}'.format(r_uint8).replace('0x','')
	g = '0x{:02x}'.format(g_uint8).replace('0x','')
	b = '0x{:02x}'.format(b_uint8).replace('0x','')
	return '#'+r+g+b

class Drawable(object):
	''' Interface for objects that can be drawn on a tkinter Canvas '''
	def draw(self,canvas):
		raise NotImplementedError

	def delete(self,canvas):
		raise NotImplementedError

class Box(Drawable):
	''' Box executes a function when moused over '''
	def __init__(self,x1,y1,x2,y2,fill='black'):
		self.x1,self.y1,self.x2,self.y2 = x1,y1,x2,y2
		self.fill = fill

	def draw(self,canvas):
		self.handle = canvas.create_rectangle(self.x1,self.y1,self.x2,self.y2, fill=self.fill)

	def delete(self,canvas):
		canvas.delete(self.handle)