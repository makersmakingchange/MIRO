from wtfj import*

class Layout(Piece):
	'''Model of what is displayed onscreen. Communication with tkpiece is first
	routed through this module.'''

	def _BEFORE_start(self):
		self.subscribe(Uid.ENGINE)
		self.subscribe(Uid.EYETRACKER)
		self.subscribe(Uid.BLINK)
		self.subscribe(Uid.TEXT)
		self.subscribe(Uid.WFACE)
		self._horizontal_division = False
		self._n_current_keys = 0
		self._last_eye = (0.0,0.0)
		self._imagenames = {}
		self._last_feedback_key = '-1,-1,-1,-1'
		self._gaze_record = RecordKeeper(1.75) #Jarrod = 1.5
		self._select_debounce_s = .75
		self._last_select = 0
		self._change_font = True
		self._speak_preview = True

	def _ON_text_buffer(self,data):
		'''Text stores the current value of the feedback buffer. Signals sent to tkpiece are
		routed through layout module.'''
		self.send_to(Uid.TKPIECE,Msg.TEXT,'feedback'+','+data)

	def _ON_eyetracker_gaze(self,data):
		'''Only record a single gaze coordinate at a time.'''
		eye_data = data.split(",")
		# Uncomment next 3 lines for filtered
		self._gaze_record.add_record(float(eye_data[0]),float(eye_data[1])) # raw eyetracker input
		mean = self._gaze_record.mean()
		self._last_eye = (mean[1],mean[2])
		# Uncomment below for unfiltered
		#self._last_eye = (float(eye_data[0]),float(eye_data[1]))
		self._generate_feedback()
	
	def _generate_feedback(self):
		'''Provides audio and visual feedback when the user has entered a new selectiona area.'''
		shapes = self.shape_list.split(",")
		for index in range(0,len(shapes)/5):
			ul = (shapes[5*index+1],shapes[5*index+2])
			br = (shapes[5*index+3],shapes[5*index+4])
			coord_string = str(ul[0]) + ',' + str(ul[1]) + ',' + str(br[0]) + ',' + str(br[1])
			if (self._contains(ul,br) == True):
				if (coord_string != self._last_feedback_key or self._speak_preview == True):
					self._speak_preview = False
					# Visual feedback goes directly to tkpiece
					self.send_to(Uid.TKPIECE,Msg.FEEDBACK, coord_string)
					# Audio feedback is routed through engine to audio
					#self.send_to(Uid.ENGINE,Msg.FEEDBACK, str(index))
					self._last_feedback_key = coord_string
					# After changing feedback, set history to center of current selection
					center_x = (float(ul[0]) + float(br[0]))/2
					center_y = (float(ul[1]) + float(br[1]))/2
					self._gaze_record.set_history(center_x,center_y)

	def _contains(self,upper_left, bottom_right):
		'''Helper function to determine if a shape contains the last
		eyetracker coordinates.'''
		# Until screen size is dynamic on eyetracker:
		ul = (float(upper_left[0]),float(upper_left[1]))
		br = (float(bottom_right[0]),float(bottom_right[1]))
		if (ul[0] < self._last_eye[0] and ul[1] < self._last_eye[1] and br[0] > self._last_eye[0] and br[1] > self._last_eye[1]):
			return True
		return False

	def _check_select(self):
		now = time.clock()
		if now - self._last_select > self._select_debounce_s:
			shapes = self.shape_list.split(",")
			for index in range(0,len(shapes)/5):
				ul = (shapes[5*index+1],shapes[5*index+2])
				br = (shapes[5*index+3],shapes[5*index+4])
				if (self._contains(ul,br) == True):
					self.send_to(Uid.ENGINE,Msg.SELECT,str(index))
		else:
			self.err('Received multiple select signals in '+str(self._select_debounce_s)+' seconds')
		self._last_select = now

	def _ON_blink_select(self,data):
		'''On short blink, check it last eye coordinate was within any keys,
		On medium and long blink, pass signal to engine to map to specialized function. Do not
		do anything on offscreen message. Represents timeout.'''
		if data == 'short':
			self._check_select()
		elif data == 'long':
			self.send_to(Uid.ENGINE,Msg.SELECT,"long")
		elif data == 'offscreen':
			self.send_to(Uid.ENGINE,Msg.SELECT,"offscreen")

	def _ON_wface_select(self,data):
		'''When a face select signal is emitted, check if the last
		eye coordinate was within any of the keys'''
		self._check_select()

	def _clear_screen(self):
		'''Before drawing anything on the screen, clear all images and keys'''
		for i in range(self._n_current_keys):
			self.send_to(Uid.TKPIECE,Req.DELETE,'key'+str(i))
		num_keys = 0
		for key in self._imagenames:
			self.send_to(Uid.TKPIECE,Req.DELETE,self._imagenames[key])
			num_keys += 1
		for i in range(num_keys):
			try:
				del self._imagenames[i]
			except KeyError:
				pass # No key present yet
		self._n_current_keys = 0

	def _divide_screen(self,n,options):
		'''Helper method that determines how to divide the screen between the number of keys (n) on the screen. Produces
		a string to represent the on screen keys in the following format: upper_left_1,bottom_right_1,upper_left_2,bottom_right_2
		such that upper_left and upper_right are tuples with the x and y coordinates of the upper left and bottom right corners of the
		shape, respectively.'''
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
			dy = .85 / (val)
			j = 1
			for x in range(0,val):
				ul = (i*dx,x*dy)
				br = (min(1,(i+1)*dx),min(1,(x+1)*dy))
				self.shape_list = self.shape_list + shape_type + "," + str(ul[0]) + "," + str(ul[1]) + "," + str(br[0]) + "," + str(br[1]) + ","
				x = (ul[0] + br[0])/2
				y = (ul[1] + br[1])/2
				width = br[0]-ul[0]
				height = br[1]-ul[1]
				# Handle images
				if options[key_counter][0] == '#':
					option = options[key_counter]
					option = option[1:]
					# Save the image handle as the option name
					self._imagenames[key_counter] = option
					# Create and draw the image
					self.send_to(Uid.TKPIECE,Req.IMAGE,option+','+str(x)+','+str(y)+','+str(width*.5)+','+str(height*.5))
				# Handle Text
				else:			
					self.send_to(Uid.TKPIECE,Req.CREATE,'text,key'+str(key_counter)+','+str(x)+','+str(y))
					# Update the value of the text field
					options[key_counter] = options[key_counter].replace('_to_',':')
					self.send_to(Uid.TKPIECE,Msg.TEXT,'key'+str(key_counter)+','+options[key_counter])
					if (key_counter == (n-1) and self._change_font == True):
						# only emit signal based on the dimensions of the last key (always the smallest)
						self._change_font = False
						self.send_to(Uid.TKPIECE,Msg.FONTSIZE,'key'+str(key_counter)+','+str(height))
				j+=1
				key_counter += 1
			i+=1
		self.shape_list = self.shape_list[0:len(self.shape_list)-1]

	def _ON_engine_options(self,data):
		'''Determine how to divide the screen based on the number of options of the curent node of the engine.
		Only display as many keys as needed. Ex: 2 engine options, only display 2 keys. 5 engine options, display
		5 keys.'''
		self._speak_preview = True
		options = data.split(',')
		# Find number of options emitted by engine
		n = len(options)
		# If those options differ from the current number of options clear the screen of options
		self._clear_screen()
		self._divide_screen(n,options)

		# Save current number of options displayed and send acknowledgement back				
		self._n_current_keys = n
		self.send(Msg.ACK)

	def _ON_engine_built(self,data):
		'''Prevents text scaling from occurring whenver the number of on screen keys changes. Instead,
		text is only scaled when the engine is built with a different number of keys.'''
		self._change_font = True

	@staticmethod
	def script():
		text_entry = [
			'@layout marco',
			'engine options #alphabet,#numbers,#nontext',
			'engine options a_to_i,j_to_r,s_to_z',
			'eyetracker gaze .1,.3',
			'eyetracker gaze .1,.7',
			'engine options spc,com,.',
			'eyetracker gaze 0,0',
			'eyetracker gaze .9,.3',
			'eyetracker gaze .9,.3',
			'eyetracker gaze .9,.3',
			'eyetracker gaze .9,.3',
			'@engine stop'
		]
		return Script(text_entry)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Layout,argv)