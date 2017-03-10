from wtfj import *
import random
import time
random.seed()


class Blink(Piece):

	def _AFTER_start(self):
		self._time_last_eye_msg_recvd = None
		self._blinked = False
		self._blink_threshold = 0.5
		self._select_val = 0

	def _ON_eyetracker_gaze(self,data):
		self._time_last_eye_msg_recvd = time.clock()
<<<<<<< HEAD
#	def _ON_gui_regions(self,data=None):
#		self.regions = data[2].split(",")
#		for x in range(len(regions)):
#			if
=======
		eye_pt = [int(x) for x in data.split(',')]
		if eye_pt[0] > 540:
			self._select_val = 1
		else:
			self._select_val = 0
>>>>>>> 122e1a3c16edb826d81bca6847bfe3ca393e0773

	def _DURING_poll(self):
		if self._time_last_eye_msg_recvd is not None:
			now = time.clock()
			delta = now - self._time_last_eye_msg_recvd
<<<<<<< HEAD
			if delta > self._blink_threshold and self._blinked is False:
				self._blinked = True
				self.send_to(Uid.ENGINE,Msg.SELECT,'0')
=======
			if delta > self._blink_threshold:
				if self._blinked is False:
					self._blinked = True
					self.send_to(Uid.ENGINE,Msg.SELECT,str(self._select_val))
>>>>>>> 122e1a3c16edb826d81bca6847bfe3ca393e0773
			else:
				self._blinked = False

	@staticmethod
	def script():

		eyes = [
			'@blink marco',
			'@blink period 0.1',
			'@blink uptime'
		]

		for i in range(0,5):
			x,y = random.randint(0,1280),random.randint(0,720)
			msg = 'eyetracker gaze '+str(x)+','+str(y)
			eyes.append(msg)

		eyes.append('@blink period 1')

		for i in range(0,5):
			x,y = random.randint(0,1280),random.randint(0,720)
			msg = 'eyetracker gaze '+str(x)+','+str(y)
			eyes.append(msg)
			eyes.append(pack(Uid.SYSTEM,Msg.IDLE,None))

		eyes.append('@blink period 0.1')

		for i in range(0,5):
			x,y = random.randint(0,1280),random.randint(0,720)
			msg = 'eyetracker gaze '+str(x)+','+str(y)
			eyes.append(msg)

		eyes.append('@blink stop')

		return Script(eyes)


if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Blink,argv,subscriptions=['eyetracker'])