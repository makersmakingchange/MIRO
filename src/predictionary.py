from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(Predictionary,argv)

class Node(dict):
	''' 
	A letter in the dict tree that has information about how often it occurs,
	links to next letters of words in the dict, and links to its parent for reverse
	traversal of the tree structure
	'''
	def __init__(self, parent=None, char=None):
		self._frequency = 1
		self._char = char
		self._parent = parent
		self._traversed = False # !!! this needs to be reset after repr called

	def __repr__(self):
		if self._parent is None:
			return '[root]'
		else:
			return '['+self._char+', '+str(self._frequency)+']'

class Predictionary(Piece):
	''' Predictive text object in the shape of a letter tree, built from a supplied .txt file '''
	
	def _BEFORE_start(self):
		''' Subscribe to engine's choices '''
		self.subscribe(Uid.ENGINE)

	def _ON_build(self,data=None):
		''' Builds the nodes in the predictive text dictionary tree '''
		if data is None:
			filename = '../dict/standard_predictionary.txt'
		else:
			filename = data
		root = self._root = Node()
		head = self._head = self._root
		next_char_root = self._next_char_root = Node()
		break_chars = [' ',':',';',',','.','\'','"','?','-','_','0','1','2','3','4','5','6','7','8','9','(',')']
		omit_chars = ['\n','\t','\r']
		self._completion_chars = [' ',',','.','?','!','spc']
		with open(filename) as f:
			last_char = ' '
			for line in f:
				for char in line:
					try:
						char = unicode(char.lower())
					except:
						break
					if char not in omit_chars:
						# Calculate next most likely char
						try:
							last_letter_node = next_char_root[last_char]
						except KeyError:
							last_letter_node = next_char_root[last_char] = Node(next_char_root, last_char)
						try:
							last_letter_node[char]._frequency += 1
						except KeyError:
							last_letter_node[char] = Node(last_char, char)
						last_char = char

						# Build dictionary tree
						if char in break_chars:
							head = self._root # Return to the top of the dictionary
							try:
								head[char]._frequency += 1
							except KeyError:
								head[char] = Node(head, char)
						else:
							try:
								head[char]._frequency += 1
							except KeyError:
								head[char] = Node(head, char)
							head = head[char] # Advance down the tree
					else:
						head = self._root
		self._all_symbols = self._get_children(self._root)
		self.send(Msg.BUILT)

	def __repr__(self):
		''' 
		Return a string of all possible words in the dictionary
		NOTE this does not return words that are the first part of a longer word,
		e.g. if 'all' is in the dictionary 'a' is not output
		TODO mark end of all words
		'''
		str_out = '<PREDICTIONARY>\n'
		for first_letter in self._root.values():
			head = first_letter
			depth = 0
			while head.parent is not None:
				if head.traversed:
					head = head.parent
					depth -= 1
				elif len(head) == 0:
					str_out += self._get_word(head) + '\n'
					head.traversed = True
				else:
					head_advanced = False
					for head_candidate in head.values():
						if head_candidate.traversed is not True:
							head = head_candidate
							head_advanced = True
							depth += 1 
					if head_advanced is False:
						head.traversed = True
		return str_out

	def _freqstrings(self):
		''' Prints letters sorted by frequency (I think? Comment your code Max) '''
		out = '<NEXT LETTER>'
		for letter_node in sorted(self._next_char_root.values(), key=lambda x: ord(x._char)):
			freq_list = ''
			for letter in sorted(letter_node.values(), key=lambda x: -x._frequency):
				freq_list += letter._char
			out += '\n'+'['+letter_node._char+']' + freq_list
		return out

	def _get_word(self, node):
		''' Walks up the tree and down to find a whole word '''
		out = node
		str_out = ''
		rev_word = []
		while(out._char is not None):
			rev_word.append(out)
			out = out.parent
		for letter in rev_word[::-1]:
			str_out += letter._char
		return str_out

	def _get_children(self, at_node=None):
		''' Gets all available choices for next letter sorted by frequency (highest first) '''
		if at_node is None: at_node = self._head
		one, twoplus = [x for x in at_node.values() if len(x) == 0], [x for x in at_node.values() if len(x) > 0]
		freq_sorted_one = sorted(one, key=lambda x: -x._frequency)
		freq_sorted_twoplus = sorted(twoplus, key=lambda x: -x._frequency)
		return ''.join([x._char for x in freq_sorted_twoplus]) + ''.join([x._char for x in freq_sorted_one])

	def _ON_engine_chose(self,data):
		''' Move down the dictionary tree if data is a valid choice. Else switch to frequency method '''
		try:
			self._head = self._head[data]
			options = ''.join([char+',' for char in self._get_children()])[:-1]
			if (options != ''):
				self.send(Msg.OPTIONS,options)
		except KeyError:
			self.err(data+' selection not available')
			self._ON_reset()

	def _get_arrangement(self):
		''' Get a list of all the available chars in the dictionary '''
		arrangement = str(self._all_symbols)
		in_words = self._get_children() if self._get_children() is not None else ''
		for char in in_words:
			arrangement = arrangement.replace(char,'')
		return in_words + '.' + arrangement

	def _ON_reset(self,data=None):
		''' Resets the dictionary tree, back to choose a new first letter '''
		self._head = self._root
		self.send(Msg.ACK)

	@staticmethod
	def script():
		script = [
			'@predictionary marco',
			'@predictionary build',
			'engine chose t',
			'engine chose z',
			'@predictionary reset',
			'engine chose l',
			'engine chose a',
			'engine chose z',
			'@predictionary stop'
		]
		return Script(script)

if __name__ == '__main__': main()
	#word = p.process(raw_input())
	#if word is not None: print('Word found: '+word)
	#print(p._get_arrangement())