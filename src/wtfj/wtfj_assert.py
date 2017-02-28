class Assert:
	''' All forms of assertion of the form Assert(b).something(a) '''
	def __init__(self,b,fail_fast=False):
		self._b = b
		self._fail_fast = fail_fast

	def fail(self,msg):
		msg = '| ASSERT.FAIL |  '+msg+'  | ASSERT.FAIL |'
		bar = ''.join(['-' for i in range(len(msg))])
		print(bar)
		print(msg)
		print(bar)
		if self._fail_fast: raise AssertionError

	def contains(self,a):
		b = self._b
		if a not in b: 
			self.fail('Tests failed, expected ['+str(a)+'] in ['+str(b)+']')
		return self

	def equals(self,a):
		b = self._b
		if a != b: 
			self.fail('Tests failed, expected ['+str(b)+'] to equal ['+str(a)+']')
		return self

	def has_csv_array_of_size(self,size=2):
		data_values = self._b.split(' ',2)[2].split(',')
		if len(data_values) != size: 
			self.fail('Data in msg ['+self._b+'] is not csv format of size '+str(size)+'')