from connectors_zmq import *
from piece import Piece
from uid import Uid
import time

# Server connections
zpub = ZmqPublisher() # Publishes messages to all subscribers
zpull = ZmqPuller() # Pulls messages fom all subscribers

# Client connections
zsub = ZmqSubscriber('test') # Filters incoming messages to uid 'test'
zpush = ZmqPusher() # Pushes messages back to server

# Block for connect
time.sleep(1)

# Test a Piece over zmq connections
p = Piece(zsub,zpush)
p.start()
zpub.send('@piece marco')

time.sleep(1)

response = zpull.poll()
assert response is not []
print(response[0])

p.stop()
