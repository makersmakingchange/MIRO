from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(Engine,argv)

letters_lc = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
numbers = ['0','1','2','3','4','5','6','7','8','9']
punctuation = ['spc','del','clr','.','com','\'','\"','?','!',';','-',':','(',')','num','$','[',']','{','}','/','\\']
menu_options = ['#keyboard','edit']
menu_handles = {}
keyboard_options = ['#alphabet','#numbers','...']
keyboard_handles = {}
edit_options = ['#save','#undo','edit']

class Engine(Piece):
	''' Letter and menu selection engine '''

	def _ON_build(self,data):
		num_options = int(data)
		if (num_options == 1):
			self.send(Msg.ERR,'1 key layout invalid\n')
		else:
			self._options = OptionNode()
			#build_non_ordered_tree(self._options,num_options,menu_options,menu_handles)
			build_non_ordered_tree(self._options,num_options,keyboard_options,keyboard_handles)
			#build_non_ordered_tree(menu_handles.get('#keyboard'),num_options,keyboard_options,keyboard_handles)
			build_ordered_tree(keyboard_handles.get('#alphabet'),num_options,letters_lc)
			build_ordered_tree(keyboard_handles.get('#numbers'),num_options,numbers)
			build_non_ordered_tree(keyboard_handles.get('...'),num_options,punctuation)
			#build_non_ordered_tree(menu_handles.get('edit'),num_options,edit_options)
			self._current_option = self._options
			self._ON_process(None)

	def _ON_select(self,data):
		selection = int(data)
		self._current_option = self._current_option.children[selection]
		self._ON_process(None)

	def _ON_process(self,data):
		msg = ''
		if len(self._current_option.children) == 0:
			if (self._current_option.content[0] != '#'):
				self.send_to(Uid.AUDIO,Req.SPEAK,self._current_option.content)
			if (self._current_option.content == "clr"):
				self.send(Msg.CHOSE, "#clear")
			elif (self._current_option.content == 'del'):
				self.send(Msg.CHOSE, "#undo")
			else:
				self.send(Msg.CHOSE, self._current_option.content)
			self._current_option = self._options
		for i in range(len(self._current_option.children)):
			msg += self._current_option.children[i].content
			if i < len(self._current_option.children)-1:
				msg += ','
		self.send(Msg.OPTIONS,msg)

	@staticmethod
	def script():
		return Script([
			'@engine marco',
			'@engine period 1',
			'@engine build 3',
			'@engine select 1',
			'@engine select 0',
			'@engine select 0',
			'@engine select 0',
			'@engine select 0',
			'@engine select 0',
			'@engine select 0',
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
				if (handles != None):
					handles[node.content] = node
				keys_to_place-=1
				key_index+=1
			next_node = OptionNode('#next')
			head.add_child(next_node)
			head = next_node
		else:
			node = OptionNode(choices[key_index])
			head.add_child(node)
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
		child.parent = self

	def add_children(self,*children):
		for child in children:
			self.add_child(child)

if __name__ == '__main__': main()