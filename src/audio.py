#import winsound
import pygame
from wtfj import *
from os import system

AUDIO_PATH = '../res/audio/'

class Audio(Piece):
	
	def _ON_speak(self,data):
		if data[0] is '#': 
			data = data[1:]
		if data in ['a_to_m','n_to_z','space','undo','next','menu','keyboard','to'] or data in 'abcdefghijklmnopqrstuvwxyz' and len(data)<=1:
			pygame.init()
			pygame.mixer.init()
			sounda = pygame.mixer.Sound(AUDIO_PATH+data+'_sound.wav')
			#winsound.PlaySound(AUDIO_PATH+data+'_sound.wav',winsound.SND_FILENAME)
			sounda.play()
		else:
			system('say '+data)

	@staticmethod
	def script():

		script = [
			'@audio uptime',
			'@audio period 1',
			'@audio marco',
			'@audio speak ab',
			#'@audio speak a_to_m',
			#'@audio speak #undo',
			#'@audio period 2',
			#'@audio speak a',
			#'@audio speak a_to_m',
			#'@audio speak #undo',
			#'@audio uptime',
			'@audio stop'
		]

		return Script(script)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Audio,argv)
