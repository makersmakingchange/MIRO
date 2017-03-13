import os
from os import listdir
from os.path import isfile, join

cwd = os.path.dirname(__file__)
pypath = cwd+'/..'
exepath = cwd+'/../../bin'

pyfiles = [f for f in listdir(pypath) if isfile(join(pypath,f))]
exefiles = [f for f in listdir(exepath) if not isfile(join(exepath,f))]

def _print(msg):
	print(msg)
	pass

with open(pypath+'/wtfj/protocol/uid.py','w') as uids:
	_print('-------------------------')
	_print('Generating uids in uid.py')
	_print('-------------------------')
	filenames = pyfiles
	filenames.extend(exefiles)
	for piece_filename in filenames:
		_print(piece_filename)
		if '.py' in piece_filename:
			parts = piece_filename.split('.')
			uid = parts[0]
		elif '.' not in piece_filename:
			uid = piece_filename
		if uid is None or uid is '':
			pass
		else:
			uid_val = uid.upper()+' = \''+uid+'\'\n'
			uids.write(uid_val)
	uids.write('PIECE = \'piece\'')

from protocol import uid as Uid
from protocol import req as Req
from protocol import msg as Msg
from protocol import mode as Mode
from protocol import tcp as Tcp

def print_bar(msg,top=True,bottom=True):
	bar = ''
	for char in msg:
		bar += '-'
	if top is True: _print(bar)
	_print(msg)
	if bottom is True: _print(bar)

def get_uid(piece):
	''' Returns id based on class name '''
	return piece.__class__.__name__.lower()

def get_attr(class_to_check):
	''' Returns strings of a class' members '''
	return [getattr(class_to_check,member) for member in dir(class_to_check) 
		if '__' not in member]

print_bar('Importing all identifiers in protocol')

valid = [Uid,Req,Msg,Mode,Tcp]
for v in valid:
	print_bar('Importing ids for ['+v.__name__+']')
	for name in dir(v):
		if '__' not in name:
			_print(name)