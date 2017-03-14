from wtfj import*

class Layout(Piece):

	def _BEFORE_start(self):
		self.subscribe(Uid.ENGINE)
		self.subscribe(Uid.EYETRACKER)
		self.subscribe(Uid.BLINK)
		self.subscribe(Uid.TEXT)
		self._horizontal_division = False
		self._n_current_keys = 0
		self._last_eye = (0.0,0.0)
		self._imagenames = {}
		self.send_to(Uid.TKPIECE,Req.CREATE,'text,feedback'+','+str(0)+','+str(0))

	def _ON_text_buffer(self,data):
		self.send_to(Uid.TKPIECE,Req.DELETE,'feedback')
		self.send_to(Uid.TKPIECE,Req.CREATE,'text,feedback'+','+str(.5)+','+str(.5))
		self.send_to(Uid.TKPIECE,Msg.TEXT,'feedback'+','+data)

	def _ON_eyetracker_gaze(self,data):
		'''Only record a single gaze coordinate at a time.'''
		eye_data = data.split(",")
		self._last_eye = (float(eye_data[0]),float(eye_data[1]))

	def _contains(self,upper_left, bottom_right):
		'''Helper function to determine if a shape contains the last
		eyetracker coordinates.'''
		# Until screen size is dynamic on eyetracker:
		ul = (float(upper_left[0]),float(upper_left[1]))
		br = (float(bottom_right[0]),float(bottom_right[1]))
		if (ul[0] < self._last_eye[0] and ul[1] < self._last_eye[1] and br[0] > self._last_eye[0] and br[1] > self._last_eye[1]):
			return True
		return False

	def _ON_blink_select(self,data):
		'''When a blink select signal is emitted, check if the last
		eye coordinate was within any of the keys'''
		shapes = self.shape_list.split(",")
		for index in range(0,len(shapes)/5):
			ul = (shapes[5*index+1],shapes[5*index+2])
			br = (shapes[5*index+3],shapes[5*index+4])
			if (self._contains(ul,br) == True):
				self.send_to(Uid.ENGINE,Msg.SELECT,str(index))
				return

	def _ON_engine_options(self,data):
		options = data.split(',')
		# Find neumber of options emitted by engine
		n = len(options)
		# If those options differ from the current number of options clear the screen of options
		if n != self._n_current_keys:
			for i in range(self._n_current_keys):
				self.send_to(Uid.TKPIECE,Req.DELETE,'key'+str(i))
			self._n_current_keys = 0
			max_rows = 5
			shape_type = "rect"
			assert(max_rows == 5)
			if (n > max_rows):
				cols = n/max_rows + (n%max_rows > 0)
			elif(n == max_rows):
				cols = n/(max_rows/2) + (n%(max_rows/2) > 0) - 1
			else:
				if (self._horizontal_division == False and n == 2):
					cols = 2;
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
			dx = 1.0 / (len(col_keys))
			i = 0
			key_counter = 0
			for val in reversed(col_keys):
				dy = 1.0 / (val)
				j = 1
				for x in range(0,val):
					ul = (i*dx,x*dy)
					br = (min(1,(i+1)*dx),min(1,(x+1)*dy))
					self.shape_list = self.shape_list + shape_type + "," + str(ul[0]) + "," + str(ul[1]) + "," + str(br[0]) + "," + str(br[1]) + ","
					x = (ul[0] + br[0])/2
					y = (ul[1] + br[1])/2
					self.send_to(Uid.TKPIECE,Req.CREATE,'text,key'+str(key_counter)+','+str(x)+','+str(y))
					j+=1
					key_counter += 1
				i+=1
			self.shape_list = self.shape_list[0:len(self.shape_list)-1]
			self._n_current_keys = n

		# For each option emitted by engine
		for i in range(n):
			# Determine the center point of the screen to draw it
			x = str((1.0+i)/(n+1))
			y = str(1.0/2)
			# If the option starts with a '#' and is displayed as an image
			if options[i][0] == '#':
				option = options[i][1:]
				try:
					# Delete old images
					self.send_to(Uid.TKPIECE,Req.DELETE,self._imagenames[i])
					del self._imagenames[i]
				except KeyError:
					pass # No key present there yet
				# Save the image handle as the option name
				self._imagenames[i] = option
				# Create and draw the image
				self.send_to(Uid.TKPIECE,Req.IMAGE,option+','+x+','+y)	
			else:
				# Create a new gui text field if options were cleared
				if self._n_current_keys == 0:
					self.send_to(Uid.TKPIECE,Req.CREATE,'text,key'+str(i)+','+x+','+y)
				# Update the value of the text field
				options[i] = options[i].replace('_to_',':')
				self.send_to(Uid.TKPIECE,Msg.TEXT,'key'+str(i)+','+options[i])

		# Save current number of options displayed and send acknowledgement back				
		self._n_current_keys = n
		self.send(Msg.ACK)

	@staticmethod
	def script():
		text_entry = [
			'@layout marco',
			'engine options a_to_b,c_to_d,e_to_f,g_to_h',
			'eyetracker gaze .3,.3',
			'blink select',
			'text buffer a',
			'eyetracker gaze .3,.7',
			'blink select',
			'eyetracker gaze .7,.3',
			'blink select',
			'text buffer a',
			'text buffer b',
			'text buffer c',
			'eyetracker gaze .7,.7',
			'blink select',
			'@layout stop'
		]
		return Script(text_entry)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Layout,argv)