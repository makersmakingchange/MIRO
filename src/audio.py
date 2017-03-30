import winsound
from wtfj import *
from os import system
import win32com.client as wincl # pip install pypiwin32

AUDIO_PATH = '../res/audio/'

speak = wincl.Dispatch("SAPI.SpVoice")
speak.Speak('')
speak.Rate = 3


class Audio(Piece):
	''' Searches for prerecorded wavs of argument passed to it. If not found calls text-to-speech conversion '''

	def _ON_speak(self,data=None):
		if data[0] is '#': data = data[1:]
		#if data in ['a_to_m','n_to_z','undo','to'] or data in 'abcdefghijklmnopqrstuvwxyz':
		#	winsound.PlaySound(AUDIO_PATH+data+'_sound.wav',winsound.SND_FILENAME)
		#else:
		#	self.err('Could not find file for argument ['+str(data)+']')			
		speak.Speak(data)

	@staticmethod
	def script():

		script = [
			'@audio uptime',
			'@audio marco',
			'@audio period 3',
			'@audio speak anything I want to say',
			'@audio speak hello my honey',
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