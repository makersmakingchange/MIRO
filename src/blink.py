from wtfj import *
import random
import time
random.seed()


class Blink(Piece):

	def _after_start(self):
		self._time_last_eye_msg_recvd = None
		self._blinked = False
		self._blink_threshold = 0.5

	def _on_eyetracker_gaze(self,data=None):
		self._time_last_eye_msg_recvd = time.clock()

	def _poll_event(self):
		if self._time_last_eye_msg_recvd is not None:
			now = time.clock()
			delta = now - self._time_last_eye_msg_recvd
			if delta > self._blink_threshold and self._blinked is False:
				self._blinked = True
				self.send(Msg.SELECT)
			else:
				self._blinked = False


if __name__ == '__main__':

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
		eyes.append(pack(Uid.SYSTEM,Msg.IDLE))

	eyes.append('@blink period 0.1')

	for i in range(0,5):
		x,y = random.randint(0,1280),random.randint(0,720)
		msg = 'eyetracker gaze '+str(x)+','+str(y)
		eyes.append(msg)

	eyes.append('@blink stop')

	Blink(Script(eyes),Printer('RECV < ')).subscribe('eyetracker').start()