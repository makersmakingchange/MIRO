import pip
res = False
try:
    import zmq
except ImportError:
    res = pip.main(['install','pyzmq'])
    import zmq

from wtfj import *

Runner.run(Uid.SYSTEM,Mode.ZSERVER)
Runner.run(Uid.TKPIECE,Mode.ZCLIENT)
Runner.run(Uid.LAYOUT,Mode.ZCLIENT)
Runner.run(Uid.ENGINE,Mode.ZCLIENT)
Runner.run(Uid.TEXT,Mode.ZCLIENT)
Runner.run(Uid.AUDIO,Mode.ZCLIENT)
Runner.run(Uid.BLINK,Mode.ZCLIENT)
Runner.run(Uid.EYETRACKER,Mode.EXE)
Runner.run(Uid.CONFIGURE,Mode.ZCLIENT)
#Runner.run(Uid.WFACE,Mode.ZCLIENT)
#Runner.run(Uid.FACE,Mode.EXE)
Runner.run(Uid.ZPRINTER,Mode.ZPRINTER)
