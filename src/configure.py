from wtfj import*

class Configure(Piece):

	def _BEFORE_start(self):
		self.subscribe(Uid.ENGINE)
		self._num_keys = 2 # default start with 2 keys
		self._engine_built = False
		self._last_msg = time.clock()
		# color schemes denoted [<text color>, <background color>, <preselect color>]
		self._color_schemes = {
			'#blackwhiteyellow' : ['#000000','#ffffff','#ffff00'],
			'#blackbluegreen' : ['black','blue','green'],
		}

	def _ON_engine_built(self,data):
		self._engine_built = True

	def _ON_engine_chose(self,data):
		'''Watch for configuration changes'''
		color_key = self._color_schemes.get(data)
		color_string = ''
		if(color_key != None):
			for i in color_key:
				color_string = color_string + i + ','
			color_string = color_string[0:len(color_string)-1]
			self.send_to(Uid.TKPIECE,Msg.CHANGECOLOR,color_string)
		else:	
			if (str(data) == '#plus'):
				self._num_keys +=1
				self.send_to(Uid.ENGINE,Msg.BUILD,str(self._num_keys))
			elif(str(data) == '#minus'):
				if (self._num_keys > 2):
					# Minimum of 2 keys
					self._num_keys-=1
				self.send_to(Uid.ENGINE,Msg.BUILD,str(self._num_keys))
			elif(str(data) == '#blinkselect'):
				self._stop_selection()
				self.send_to(Uid.SYSTEM,Msg.START,'blink')
			elif(str(data) == '#faceselect'):
				self._stop_selection()
				self.send_to(Uid.SYSTEM,Msg.START,'wface')
				self.send_to(Uid.SYSTEM,Msg.START,'face exe')

	def _stop_selection(self):
		self.send_to(Uid.BLINK,"stop")
		self.send_to(Uid.FACE,"stop")
		self.send_to(Uid.WFACE,"stop")

	def _DURING_poll(self):
		'''Tell engine to build every 2 seconds until it is built'''
		now = time.clock()
		if (self._engine_built == False and now > self._last_msg + 2):
			self.send_to(Uid.ENGINE,Msg.BUILD,str(self._num_keys))
			self._last_msg = time.clock()

	@staticmethod
	def script():
		text_entry = [
		'@configure period 1',
		'@configure marco',
		'@configure marco',
		'engine built',
		'engine chose #plus',
		'engine chose #plus',
		'engine chose #plus',
		'engine chose #blackbluegreen',
		'engine chose #minus',
		'engine chose #faceselect',
		'engine chose #blinkselect',
		'@configure stop'
		]
		return Script(text_entry)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Configure,argv)