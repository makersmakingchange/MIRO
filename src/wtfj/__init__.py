# For future compatibility with python 3
from __future__ import print_function
from __future__ import unicode_literals
# Python imports
import sys
from threading import Thread,Lock
# Third-party imports
from uid import *
from piece import *
from connectors_local import *
from wtfj_assert import *

def make_color(r_uint8,g_uint8,b_uint8):
	''' Color in 24-bit RGB format to '0x#######' string format '''
	r = '0x{:02x}'.format(r_uint8).replace('0x','')
	g = '0x{:02x}'.format(g_uint8).replace('0x','')
	b = '0x{:02x}'.format(b_uint8).replace('0x','')
	return '#'+r+g+b
