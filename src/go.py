from wtfj import *
from genericpiece import *

#wtfj_utils.nuclear_option()

try:
	Runner.run(Uid.ZSERVER)
	Runner.run(Uid.ZPRINTER)
	Runner.run(Uid.TKPIECE,Mode.ZCLIENT)
	Runner.run(Uid.ZCONSOLE)
except Exception as e:
	print(repr(e))