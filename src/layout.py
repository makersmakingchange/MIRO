from wtfj import*

class Layout(Piece):
	@staticmethod
	def get_test_script():
		script = [
			"@layout marco",
			"@layout bs",
			"@layout stop"
		]
		return script
	def _ON_build(self,data):
		print(data)


if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Layout,argv)