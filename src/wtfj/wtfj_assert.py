''' Assertion for messaging packets '''
''' Auth: max@embeddedprofessional.com '''

import atexit # Calls exit success or fail function if one assert made 
import traceback

class WtfjError(Exception):
	pass

class Assert:
	''' All forms of assertion of the form Assert(b).something(a).etc()... '''

	_cnt = 0
	_failed = 0
	
	@staticmethod
	def _success():
		failed = str(Assert._failed)
		count = str(Assert._cnt)
		if Assert._failed > 0:
			Assert._print_msg(failed+' of '+count+ ' assertions failed','test failed')
		else:
			Assert._print_msg(count+' of '+count+' assertions passed','great success')
		return Assert._failed

	@staticmethod
	def _print_msg(msg,alert='notification',trace=None):
		label = '|| '+alert.upper()+' ||' 
		msg =  label+'  '+msg
		bar = ''.join(['-' for i in range(len(label))])
		bar = '++'+bar[:-4]+'++'
		print(bar)
		print(msg)
		print(bar)

		#if trace is not None:
		#	for line in trace:
		#		print(line)

	def __init__(self,b):
		self._b = b
		self._fail_fast = False
		if Assert._cnt is 0:
			atexit.register(Assert._success)

	def fast(self):
		self._fail_fast = True
		return self

	def fail(self):
		self._fail('Intentional failure')

	def _pass(self,msg):
		Assert._cnt +=1 
		Assert._print_msg(msg,'assert '+str(Assert._cnt)+' passed')

	def _fail(self,msg):
		Assert._cnt += 1
		Assert._failed += 1
		trace = None
		try:
			raise WtfjError
		except:
			trace = traceback.format_exc().splitlines()
			Assert._print_msg(msg,'assert '+str(Assert._cnt)+' fail',trace)
			if self._fail_fast: raise WtfjError
			pass

	def contains(self,*args):
		b = self._b
		try:
			for a in args:
				if a in b:
					self._pass('['+str(b)+'] contains ['+str(a)+']')
					return self
		except:
			pass
		self._fail('['+str(b)+'] does not contain ['+str(a)+']')
		return self

	def equals(self,a):
		b = self._b
		if a != b: 
			self._fail('Expected ['+str(b)+'] to equal ['+str(a)+']')
		else:
			self._pass('['+str(b)+'] equals ['+str(a)+']')
		return self

	def not_equal(self,a):
		b = self._b
		if a == b: 
			self._fail('Expected ['+str(b)+'] not to equal ['+str(a)+']')
		else:
			self._pass('['+str(b)+'] does not equal ['+str(a)+']')
		return self

	def sent_by(self,a):
		b = self._b
		data_values = self._b.split(' ')
		if a != data_values[0]:
			self._fail('['+b+'] not sent by ['+a+']')
		else:
			self._pass('['+b+'] sent by ['+a+']')
		return self

	def sent_to(self,a):
		b = self._b
		data_values = b.split(' ')
		if '@'+a != data_values[0]:
			self._fail('['+b+'] Not sent to ['+a+']')
		else:
			self._pass('['+b+'] sent to ['+a+']')
		return self

	def topic_is(self,a):
		topic = self._b.split(' ')[1]
		if topic == a:
			self._pass('Topic equals ['+str(a)+']')
		else:
			self._fail('Topic '+str(topic)+' does not equal ['+str(a)+']')
		return self

	def data_is_csv_size(self,size):
		try:
			data_values = self._b.split(' ',2)[2].split(',')
			if len(data_values) != size: 
				msg = 'Data in msg ['+str(self._b)+'] is not csv format of size '+str(size)+''
				self._fail(msg)
			else:
				msg = 'Data in msg ['+str(self._b)+'] is csv format of size '+str(size)+''
				self._pass(msg)
		except AttributeError:
			self._fail(msg)
		return self

	def data_equals(self,a):
		data = self._b.split(' ',2)[2]
		if data == a:
			self._pass('Data equals ['+str(a)+']')
		else:
			self._fail('Data ['+str(data)+'] does not equal ['+str(a)+']')
		return self

if __name__ == '__main__': # Examples of testing
	
	print('First 6 tests here should pass\n')
	a = Assert('abc ijk x,y,z').contains('a','j','y')
	a.equals('abc ijk x,y,z').sent_by('abc')
	a.topic_is('ijk').data_equals('x,y,z').data_is_csv_size(3)

	print('\nNext test should fail\n')
	a.fail()
	
	print('\nNext test should fail, throwing an exception error\n')
	err = ''
	try:
		a.fast().equals(None)
	except WtfjError as e:
		err = e
	Assert(repr(err)).equals('WtfjError()')

	print('\nYou should see a fail message\n')
	Assert._success() # Fails
	
	Assert._failed = 0
	print('\nReset fail count, you should see a success message on exit\n')