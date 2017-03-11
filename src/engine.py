from wtfj import *

def main():
	from sys import argv
	Runner.run_w_cmd_args(Engine,argv)

choices = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
menu_options = ['#menu','#keyboard','#undo']

def build_menu(head,num_keys,choices):
	menu = OptionNode('#menu')
	next = OptionNode('#next')
	next2 = OptionNode('#next')
	next3 = OptionNode('#next')
	undo = OptionNode('#undo')
	keyboard = OptionNode('#keyboard')
	head.add_child(undo)
	head.add_child(next)
	next.add_child(keyboard)
	next.add_child(menu)
	#next3.add_child(keyboard)
	#next3.add_child(head)
	return head


class Engine(Piece):
	''' Letter and menu selection engine '''

	def _ON_build(self,data):
		self._options = OptionNode()
		num_options = int(data)
		#build_menu(self._options,num_options,choices)
		build_tree(self._options,num_options,choices)
		self._current_option = self._options
		self._ON_process(None)

	def _ON_select(self,data):
		selection = int(data)
		self._current_option = self._current_option.children[selection]
		self._ON_process(None)

	def _ON_process(self,data):
		msg = ''
		if len(self._current_option.children) == 0:
			self.send_to(Uid.AUDIO,Req.SPEAK,self._current_option.content)
			#push.send_string('@gui write=' +current_option.content)
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
			'@engine process',
			'@engine build 3',
			'@engine select 0',
			'@engine stop'
		])

# Given root of options tree, build tree such that each node has num_keys child nodes consisting of divided choices list.
def build_tree(head,num_keys,choices):
	if len(choices) == 1:
		return
	elif len(choices) < num_keys:
		for x in range((num_keys - len(choices))):
			choices.append("#empty")
		for opt_str in choices:
			head.add_child(OptionNode(opt_str))
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
			build_tree(opt, num_keys, opt_list)

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