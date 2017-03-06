from wtfj import*

class Layout(Piece):

	def _BEFORE_start(self):
		self.subscribe(Uid.ENGINE)
		self._n_current_keys = 0

	def _ON_engine_options(self,data):
		options = data.split(',')
		n = len(options)
		if n != self._n_current_keys:
			for i in range(self._n_current_keys):
				self.send_to(Uid.TKPIECE,Req.DELETE,'key'+str(i))
			self._n_current_keys = 0
		n_col = int(n**0.5)
		n_row = int(n**0.5)
		for i in range(n):
			y = str((1.0+i)/(n+1))
			x = str(1.0/2)
			if self._n_current_keys == 0:
				self.send_to(Uid.TKPIECE,Req.CREATE,'text,key'+str(i)+','+x+','+y)
			self.send_to(Uid.TKPIECE,Msg.TEXT,'key'+str(i)+','+options[i])
		self._n_current_keys = n
		self.send(Msg.ACK)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Layout,argv)