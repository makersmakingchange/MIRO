from wtfj import*

class Layout(Piece):

	def _BEFORE_start(self):
		self.subscribe(Uid.ENGINE)
		self.subscribe(Uid.EYETRACKER)
		self._n_current_keys = 0
		self._imagenames = {}

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
				self.send_to(Uid.TKPIECE,Msg.TEXT,'key'+str(i)+','+options[i])

		# Save current number of options displayed and send acknowledgement back				
		self._n_current_keys = n
		self.send(Msg.ACK)

	@staticmethod
	def script():
		text_entry = [
			'@layout marco',
			'engine options 1,2,3,4',
			'@layout stop'
		]
		return Script(text_entry)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Layout,argv)