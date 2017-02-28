from wtfj import *

class Eyetracker(ClientPiece):
    def _on_repeat(self):
        self.send('gaze','1280,800')
        time.sleep(0.01)
        self.send_to('eyetracker','repeat')

    def _after_start(self):
        self.add_interest('eyetracker')
        self.send('repeat')

class Blink2(ClientPiece):
    def _on_eyetracker_gaze(self, data):
        self.send('got',data)
    
    def _after_start(self):
        self.add_interest('eyetracker')
        
server = ServerPiece(echo=True)
server.add_subscriber('@'+Uids.BLINK)
server.add_subscriber('@eyetracker')

Eyetracker(Uids.EYETRACKER).start(server,server)
server.publish('@eyetracker repeat ')
time.sleep(1)
recvd = None
while recvd is None:
    recvd = server.poll()
server.publish('@eyetracker stop ')
quit()






Eyetracker(Uids.EYETRACKER).start(server,server)
Assert(server.poll()).equals(Uids.EYETRACKER+' started ')
Assert(server.poll()).equals('eyetracker gaze 1280,800')
time.sleep(1)
Blink2(Uids.BLINK).start(server,server)

Assert(server.poll()).equals(Uids.BLINK + ' started ')
Assert(server.poll()).equals('blink got 1280,800')
server.publish('@'+Uids.BLINK+ ' stop ')
Assert(server.poll()).equals(Uids.BLINK + ' stopping ')

server.publish('@'+Uids.EYETRACKER + ' stop ')
Assert(server.poll()).equals(Uids.EYETRACKER+' stopping ')
try:
    server.poll(10)
except:
    quit()

