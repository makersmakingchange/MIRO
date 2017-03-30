from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(Engine,argv)

letters_lc = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
numbers = ['0','1','2','3','4','5','6','7','8','9']
punctuation = ['spc','#delete','.','com','\'','\"','?','!',';','-',':','(',')','num','$','[',']','{','}','/','\\']
menu_options = ['#keyboard','#revise','#configure']
menu_handles = {}
keyboard_options = ['#alphabet','#numbers','#nontext','#speak']
keyboard_handles = {}
edit_options = ['#clear','#review','#save', '#editdisk']
configuration_options = ['#numberkeys','#colorscheme']
configuration_options_handles = {}
numkeys_options = ['#plus','#minus']
colorscheme_options = ['#blackwhiteyellow','#blackbluegreen']

class Engine(Piece):
	''' Letter and menu selection engine '''

	def _BEFORE_start(self):
		''' Set last selection to None, subscribe to predictionary for priority options '''
		self._last_content = None
		self.subscribe(Uid.PREDICTIONARY)
		self._predictionary_head = OptionNode('predictionary')

	def _ON_build(self,data):
		''' 
		Builds the internal tree structure that holds choices for letters, and menu items, referred to 
		generically as options, using the OptionNode class as tree nodes. The command '@engine build 2'
		builds an option tree with at most two options on the screen, so selecting the '#alphabet' option
		would then break the alphabet into a binary tree, with the first two options being 'a_to_m' and
		'a_to_z'.
		
		Menu items and actions are prefaced with the '#' character, letters and other characters are 
		represented as ASCII symbols.
		
		A range of letters is represented by joining the first and last letters with '_to_', e.g. 'a_to_m'.

		Options are presented to other Pieces by emitting the signal 'engine options option1,option2,option2' 
		e.g. with a binary tree after selecting 'a_to_m' the engine would emit 'engine options a_to_g,h_to_m'.

		Selections are made from the engine by issuing the command 'engine select N', with N being a number
		from 0 to the number of options available, e.g. 'engine select 0' selects the first option available,
		usually the left and upper-most option if a GUI is present in the system.
		'''
		num_options = int(data)
		if (num_options == 1):
			self.err('1 key layout invalid')
		else:
			self._options = OptionNode()
			build_non_ordered_tree(self._options,num_options,menu_options,menu_handles)
			build_non_ordered_tree(menu_handles.get('#keyboard'),num_options,keyboard_options,keyboard_handles)
			build_ordered_tree(keyboard_handles.get('#alphabet'),num_options,letters_lc)
			build_ordered_tree(keyboard_handles.get('#numbers'),num_options,numbers)
			build_non_ordered_tree(keyboard_handles.get('#nontext'),num_options,punctuation)
			build_non_ordered_tree(menu_handles.get('#revise'),num_options,edit_options)
			build_non_ordered_tree(menu_handles.get('#configure'),num_options,configuration_options,configuration_options_handles)
			build_non_ordered_tree(configuration_options_handles.get('#numberkeys'),num_options,numkeys_options)
			build_non_ordered_tree(configuration_options_handles.get('#colorscheme'),num_options,colorscheme_options)
			self._current_option = self._options
			self._ON_process(None)
			self.send(Msg.BUILT,str(num_options))

	def _ON_feedback(self,data):
		phrase = self._current_option.children[int(data)].content.replace('_',' ')
		self.send_to(Uid.AUDIO,Req.SPEAK,phrase)

	def _undo (self):
		'''Move to parent of current node'''
		if (self._current_option.parent != None):
			self._current_option = self._current_option.parent
			self._send_options()

	def _ON_select(self,data):
		'''Process blink data. If blink is short (else condition), act as standard select and work down tree.
		If blink is medium, undo last action, if blink is long, travel back to root'''
		if data == 'long':
			self._undo()
		elif data == 'offscreen':
			self._current_option = self._options
			self._send_options()
		else:
			selection = int(data)
			self._current_option = self._current_option.children[selection]
			self._ON_process(None)

	def _send_options(self):
		msg = ''
		for i in range(len(self._current_option.children)):
			msg += self._current_option.children[i].content
			if i < len(self._current_option.children)-1:
				msg += ','
		self.send(Msg.OPTIONS,msg)

	def _ON_predictionary_options(self,data):
		options = data.split(',')
		predict = OptionNode('#predict')
		next_opt = OptionNode('#next')
		next_opt.add_child(keyboard_handles.get('#keyboard'))
		predict.add_child(OptionNode(options[0]))
		predict.add_child(next_opt)
		self._current_option = predict
		self._send_options()
		#self.send(Msg.ACK,'Got predict options')

	def _ON_process(self,data):
		if len(self._current_option.children) == 0:
			if (self._current_option.content[0] != '#'):
				self.send_to(Uid.AUDIO,Req.SPEAK,self._current_option.content)
			self.send(Msg.CHOSE, self._current_option.content)
			self._last_content = self._current_option.content
			if (self._last_content in letters_lc or self._last_content in numbers or self._last_content in punctuation or self._last_content == '#speak'):
				self._current_option = menu_handles.get('#keyboard')
			else:
				self._current_option = self._options
		self._send_options()

	@staticmethod
	def script():
		return Script([
			'@engine marco',
			'@engine period 1',
			'@engine build 3',
			'@engine select 0',
			'@engine select 1',
			'@engine select 1',
			'@engine select 0',
			'@engine select 1',
			'@engine select long',
			'predictionary options r',
			'predictionary options a,z',
			'@engine stop'
		])

def build_ordered_tree(head,num_keys,choices):
	'''Given root of options tree, build tree such that each node has num_keys child nodes consisting of divided choices list.
	Use this function for choices with logical ordering Ex: alphabet or number keys'''
	if len(choices) == 1:
		return
	elif len(choices) < num_keys:
		for option in choices:
			opt = OptionNode(option)
			head.add_child(opt)
			opt.add_parent(head)
		return
	else:
		seed_value = int(len(choices)/num_keys) + (len(choices) % num_keys > 0) # Rounds decimal results up to nearest int
		size_of_nodes = []
		for x in range(num_keys):
			size_of_nodes.append(seed_value)
		index = num_keys - 1
		while (sum(size_of_nodes) > len(choices)):
			size_of_nodes[index] = size_of_nodes[index] - 1
			index = index - 1
		option_lists = []
		sum_vals = 0
		for size in size_of_nodes:
			option = choices[sum_vals:sum_vals+size]
			option_lists.append(option)
			sum_vals = sum_vals + size
		for opt_list in option_lists:
			if (len(opt_list) > 1):
				opt_str = opt_list[0] + "_to_" + opt_list[len(opt_list)-1]
			else:
				opt_str = opt_list[0]
			opt = OptionNode(opt_str)
			head.add_children(opt)
			opt.add_parent(head)
			build_ordered_tree(opt, num_keys, opt_list)

def build_non_ordered_tree(head,num_keys,choices,handles=None):
	''' Builds tree for choices that do not follow a logical order. Example: punctuation, menu options.
	An optional paramater 'handles' can be passed to make building subsequent trees easier. '''
	original_head = head
	keys_to_place = len(choices)
	key_index = 0
	while(keys_to_place != 0):
		if (keys_to_place > num_keys):
			for j in range(num_keys-1):
				node = OptionNode(choices[key_index])
				head.add_child(node)
				node.add_parent(head)
				if (handles != None):
					handles[node.content] = node
				keys_to_place-=1
				key_index+=1
			next_node = OptionNode('#next')
			head.add_child(next_node)
			next_node.add_parent(head)
			head = next_node
		else:
			node = OptionNode(choices[key_index])
			head.add_child(node)
			node.add_parent(head)
			if (handles != None):
				handles[node.content] = node
			keys_to_place-=1
			key_index+=1
	return original_head

# Used to debug
def print_tree(head):
	print(head.content)
	for child in head.children:
		print_tree(child)

class OptionNode(object):
	def __init__(self,content=None):
		self.parent = None
		self.children = []
		self.content = content

	def add_child(self,child):
		self.children.append(child)

	def add_children(self,*children):
		for child in children:
			self.add_child(child)

	def add_parent(self,parent):
		self.parent = parent

if __name__ == '__main__': main()