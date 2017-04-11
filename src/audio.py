import winsound
from wtfj import *
from os import system
try:
        import win32com.client as wincl # pip install pypiwin32
except ImportError:
        import pip
        pip.main(['install','pypiwin32'])
        import win32com.client as wincl

AUDIO_PATH = '../res/audio/'

#speak = wincl.Dispatch("SAPI.SpVoice")
#speak.Speak('')
#speak.Rate = 10


class Audio(Piece):
	''' Searches for prerecorded wavs of argument passed to it. If not found calls text-to-speech conversion '''

	def _BEFORE_start(self):
		self.speak = wincl.Dispatch("SAPI.SpVoice")
		self.speak.Speak('')
		self.speak.Rate = 3
		self._current_rate = 3

	def _ON_speed(self,data):
		if (data == 'faster'):
			self.speak.Rate = self._current_rate + 1
			self._current_rate = self._current_rate + 1
		elif (data == 'slower'):
			if (self.speak.Rate > 1):
				self.speak.Rate = self._current_rate - 1
				self._current_rate = self._current_rate - 1

	def _ON_speak(self,data=None):
		if data[0] is '#': data = data[1:]
		#if data in ['a_to_m','n_to_z','undo','to'] or data in 'abcdefghijklmnopqrstuvwxyz':
		#	winsound.PlaySound(AUDIO_PATH+data+'_sound.wav',winsound.SND_FILENAME)
		#else:
		#	self.err('Could not find file for argument ['+str(data)+']')			
		self.speak.Speak(data)

	@staticmethod
	def script():

		script = [
			'@audio uptime',
			'@audio marco',
			'@audio period 2',
			'@audio speak anything I want to say',
			'@audio speak hello my honey',
			'@audio speed faster',
			'@audio speak hello my honey',
			'@audio speed faster',
			'@audio speak hello my honey',
			'@audio speed faster',
			'@audio speak hello my honey',
			'@audio speed faster',
			'@audio speak hello my honey',
			'@audio speed faster',
			'@audio speak hello my honey',
			'@audio speed slower',
			'@audio speak hello my honey',
			'@audio speed slower',
			'@audio speak hello my honey',
			'@audio speed slower',
			'@audio speak hello my honey',
			'@audio speed slower',
			'@audio speak hello my honey',
			'@audio speed slower',
			'@audio speak hello my honey',
			'@audio speed slower',
			'@audio speak hello my honey',
			'@audio speed slower',
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
