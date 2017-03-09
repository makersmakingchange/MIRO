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

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Layout,argv)