import winsound
from wtfj import *

AUDIO_PATH = '../res/audio/'

class Audio(Piece):
	
	def _ON_speak(self,data=None):
		if data[0] is '#': data = data[1:]
		if data in ['a_to_m','n_to_z','space','undo'] or data in 'abcdefghijklmnopqrstuvwxyz':
			winsound.PlaySound(AUDIO_PATH+data+'_sound.wav',winsound.SND_FILENAME)
		else:
			self.err('Could not find file for argument ['+str(data)+']')

	@staticmethod
	def script():

		script = [
			'@audio uptime',
			'@audio period 1',
			'@audio marco',
			'@audio speak a',
			'@audio speak a_to_m',
			'@audio speak #undo',
			'@audio period 0.2',
			'@audio speak a',
			'@audio speak a_to_m',
			'@audio speak #undo',
			'@audio uptime',
			'@audio stop'
		]

		return Script(script)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Audio,argv)
