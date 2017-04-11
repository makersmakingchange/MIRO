from wtfj import *
from os import system
import win32com.client as wincl # pip install pypiwin32 if not available

AUDIO_PATH = '../res/audio/'


class Audio(Piece):
	''' Calls text-to speech '''

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