from wtfj import *

try:
	Runner.run(Uid.SYSTEM,Mode.ZSERVER)
	Runner.run(Uid.ZPRINTER)
	#Runner.run(Uid.ZSCRIPT,Mode.ZCLIENT) $$$$ NO NO NO
	#Runner.run(Uid.TKPIECE,Mode.ZCLIENT)
	#Runner.run(Uid.ENGINE,Mode.ZCLIENT)
	#Runner.run(Uid.AUDIO,Mode.ZCLIENT)
	Runner.run(Uid.ZCONSOLE)
except Exception as e:
	print(repr(e))