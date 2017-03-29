from wtfj import *
import random
import time
random.seed()


class Blink(Piece):

	def _AFTER_start(self):
		self._time_last_eye_msg_recvd = None
		self._delta = 0
		self._blinked = False
		self._blink_threshold_short = .5
		self._blink_threshold_long = 2
		self._blink_threshold_offscreen = 8
		self._select_val = 0

	def _ON_eyetracker_gaze(self,data):
		# Blink module only needs to detect blink (based on time without coords)
		if (self._delta > self._blink_threshold_offscreen):
			self.send(Msg.SELECT,"offscreen")
			self._delta = 0
		elif (self._delta > self._blink_threshold_long):
			self.send(Msg.SELECT,"long")
			self._delta = 0
		elif (self._delta > self._blink_threshold_short):
			self.send(Msg.SELECT,"short")
			self._delta = 0
		self._time_last_eye_msg_recvd = time.clock()

	def _DURING_poll(self):
		if self._time_last_eye_msg_recvd is not None:
			now = time.clock()
			self._delta = now - self._time_last_eye_msg_recvd

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