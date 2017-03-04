from wtfj import Uid,Mode,Runner

#Runner.run(Uid.CONSOLE,Mode.INTERACTIVE)
Runner.run(Uid.TKPIECE,Mode.CLIENT_ZMQ)
Runner.run(Uid.OUTPUT,Mode.PRINTER_ZMQ)
#Runner.run(Uid.AUDIO,Mode.TEST)
#Runner.run(Uid.BLINK,Mode.TEST)
#run_piece(Uid.AUDIO,Mode.LOCAL)
#run_piece(Uid.EYETRACKER,Mode.EXE)