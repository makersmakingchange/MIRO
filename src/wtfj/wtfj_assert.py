''' Assertion for messaging packets '''
''' Auth: max@embeddedprofessional.com '''

class Assert:
	''' All forms of assertion of the form Assert(b).something(a).etc()... '''

	_cnt = 0

	@staticmethod
	def success():
		msg = '| SUCCESS |  all Assertions passed  | SUCCESS |'
		bar = ''.join(['-' for i in range(len(msg))])
		print(bar)
		print(msg)
		print(bar)

	def __init__(self,b):
		self._b = b
		self._fail_fast = False

	def fast(self):
		self._fail_fast = True
		return self

	def fail(self):
		self._fail('intentional failure')

	def _pass(self):
		Assert._cnt +=1 
		print('ASSERT '+str(Assert._cnt)+' PASSED')

	def _fail(self,msg):
		Assert._cnt += 1
		msg = '| ASSERT '+str(Assert._cnt)+' FAIL |  '+msg+'  | ASSERT '+str(Assert._cnt)+' FAIL |'
		bar = ''.join(['-' for i in range(len(msg))])
		print(bar)
		print(msg)
		print(bar)
		if self._fail_fast: raise AssertionError

	def contains(self,*args):
		b = self._b
		try:
			for a in args:
				if a in b:
					self._pass()
					return self
		except:
			pass
		self._fail('['+str(b)+'] does not contain ['+str(a)+']')
		return self

	def equals(self,a):
		b = self._b
		if a != b: 
			self._fail('expected ['+str(b)+'] to equal ['+str(a)+']')
		else:
			self._pass()
		return self

	def not_equal(self,a):
		b = self._b
		if a == b: 
			self._fail('expected ['+str(b)+'] not to equal ['+str(a)+']')
		else:
			self._pass()
		return self

	def sent_by(self,a):
		b = self._b
		data_values = self._b.split(' ')
		if a != data_values[0]:
			self._fail('not sent by ['+a+']')
		else:
			self._pass()
		return self

	def sent_to(self,a):
		b = self._b
		data_values = self._b.split(' ')
		if '@'+a != data_values[0]:
			self._fail('not sent by ['+a+']')
		else:
			self._pass()
		return self

	def topic_is(self,a):
		if self._b.split(' ')[1] == a:
			self._pass()
		else:
			self._fail('message does not equal ['+str(a)+']')
		return self

	def data_is_csv_size(self,size):
		msg = 'data in msg ['+str(self._b)+'] is not csv format of size '+str(size)+''
		try:
			data_values = self._b.split(' ',2)[2].split(',')
			if len(data_values) != size: 
				self._fail(msg)
			else:
				self._pass()
		except AttributeError:
			self._fail(msg)
		return self

	def data_equals(self,a):
		data = self._b.split(' ',2)[2]
		if data == a:
			self._pass()
		else:
			self._fail('data does not equal ['+str(a)+']')
		return self

if __name__ == '__main__': # Examples of testing
	
	# All these pass
	a = Assert('abc ijk x,y,z').contains('a','j','y')
	a.equals('abc ijk x,y,z').sent_by('abc')
	a.topic_is('ijk').data_equals('x,y,z')

	# This one fails without throwing AssertionError
	a.data_is_csv_size(3).fail()
	
	# This would throw an AssertionError upon failure
	#a.fast().equals(None)
	
	# Great success
	Assert.success()

