from wtfj import*

class Layout(Piece):
	@staticmethod
	
	def script():
		script = [
			"@layout marco",
			"@layout build something",
			"@layout stop"
		]
		return Script(script)

	def _ON_build(self,data):
		self.send(Msg.ACK)


if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Layout,argv)