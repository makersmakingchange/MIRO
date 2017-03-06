# See wtfj/__init__.py for full list of imports
from wtfj import *

# Constants and stable vars
SOCKET_SUB = 'tcp://localhost:5556'
SOCKET_PUSH = 'tcp://localhost:5557'
topic_filter = '@engine'
topic_audio = '@audio'
topic_gui = '@gui opt='

# Connect to sockets
context = zmq.Context()
push = context.socket(zmq.PUSH)
sub = context.socket(zmq.SUB)
push.connect(SOCKET_PUSH)
sub.connect(SOCKET_SUB)

if isinstance(topic_filter,bytes):
	topic_filter = topic_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,topic_filter)

letter_choices = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
number_choices = ['0','1','2','3','4','5','6','7','8','9',]
formatting_choices = ['spc','.']

# Given root of options tree, build tree such that each node has num_keys child nodes consisting of divided choices list.
def build_tree(head, num_keys, choices):
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


# Function nodes
undo = OptionNode('#undo')
speak = OptionNode('#speak')
number_of_keys = 2

root = OptionNode()
letters = OptionNode('a_to_z')
non_text = OptionNode('#_to_$')
numbers = OptionNode('0_to_9')
formatting = OptionNode('spc_to_.')

build_tree(letters, number_of_keys, letter_choices)
build_tree(numbers, number_of_keys, number_choices)
build_tree(formatting, number_of_keys, formatting_choices)
root.add_children(letters,non_text)

root_blank_keys = number_of_keys - 2
for i in range(root_blank_keys):
	root.add_child(OptionNode("#empty"))
non_text.add_children(numbers,formatting)

def command(cmd_string):
	if cmd_string == 'quit':
		quit()
	elif cmd_string == 'refresh':
		process_selection()

current_option = root
gui_msg = ''

def process_selection():
	global current_option
	gui_msg = topic_gui
	if len(current_option.children) == 0:
		if (current_option.content != 'spc'):
			push.send_string(topic_audio+' '+current_option.content)
		push.send_string('@gui write=' +current_option.content)
		current_option = root
	for i in range(len(current_option.children)):
		gui_msg += current_option.children[i].content
		if i < len(current_option.children)-1:
			gui_msg += ','
	push.send_string(gui_msg)

def select(sel_string):
	global current_option
	try:
		sel = int(sel_string)
		current_option = current_option.children[sel]
		process_selection()
	except IndexError:
		pass
	except ValueError:
		pass

def option(opt_string):
	pass

function_dict = {}
function_dict['cmd'] = command
function_dict['sel'] = select
function_dict['opt'] = option

process_selection()

while True:
	string = sub.recv_string()
	parts = string.split()
	if len(parts) > 0:
		msg_parts = parts[1].split('=')
		if len(msg_parts) > 0:
			try:
				function_dict[msg_parts[0]](msg_parts[1])
			except KeyError:
				pass