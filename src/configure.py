from wtfj import*

class Configure(Piece):

	def _BEFORE_start(self):
		self.subscribe(Uid.ENGINE)
		self._num_keys = 2 # default start with 2 keys
		self._engine_built = False
		self._last_msg = time.clock()

	def _ON_engine_built(self,data):
		self._engine_built = True

	def _ON_engine_chose(self,data):
		'''Watch for configuration changes'''
		if (str(data) == '#plus'):
			self._num_keys +=1
		elif(str(data) == '#minus'):
			if (self._num_keys > 2):
				# Minimum of 2 keys
				self._num_keys-=1
		self.send_to(Uid.ENGINE,Msg.BUILD,str(self._num_keys))

		pass # stub

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
		'engine chose #minus',
		'engine chose #minus',
		'engine chose #minus',
		'engine chose #minus',
		'engine chose #minus',
		'@configure stop'
		]
		return Script(text_entry)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Configure,argv)