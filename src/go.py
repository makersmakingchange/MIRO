from wtfj import *

try:
	Runner.run(Uid.SYSTEM,Mode.ZSERVER)
	Runner.run(Uid.ZCONSOLE)
	Runner.run(Uid.ZPRINTER)
except Exception as e:
	print(repr(e))