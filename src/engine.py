# For future compatibility with python 3
from __future__ import print_function
from __future__ import unicode_literals
# Third-party imports
import zmq

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

choices = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

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
			#print(opt_str)
			opt = OptionNode(opt_str)
			head.add_children(opt)
			build_tree(opt, num_keys, opt_list)

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


options = OptionNode()

# Function nodes
undo = OptionNode('#undo')
speak = OptionNode('#speak')

# Single letter nodes
a = OptionNode('a')
b = OptionNode('b')
c = OptionNode('c')
d = OptionNode('d')
e = OptionNode('e')
f = OptionNode('f')
g = OptionNode('g')
h = OptionNode('h')
i = OptionNode('i')
j = OptionNode('j')
k = OptionNode('k')
l = OptionNode('l')
m = OptionNode('m')
n = OptionNode('n')
o = OptionNode('o')
p = OptionNode('p')
q = OptionNode('q')
r = OptionNode('r')
s = OptionNode('s')
t = OptionNode('t')
u = OptionNode('u')
v = OptionNode('v')
w = OptionNode('w')
x = OptionNode('x')
y = OptionNode('y')
z = OptionNode('z')

# Binary search nodes
a_to_m = OptionNode('a_to_m')
a_to_f = OptionNode('a_to_f')
a_to_c = OptionNode('a_to_c')
b_to_c = OptionNode('b_to_c')
d_to_f = OptionNode('d_to_f')
e_to_f = OptionNode('e_to_f')
g_to_m = OptionNode('g_to_m')
g_to_i = OptionNode('g_to_i')
g_to_h = OptionNode('g_to_h')
j_to_m = OptionNode('j_to_m')
j_to_k = OptionNode('j_to_k')
l_to_m = OptionNode('l_to_m')
n_to_z = OptionNode('n_to_z')
n_to_s = OptionNode('n_to_s')
n_to_p = OptionNode('n_to_p')
n_to_o = OptionNode('n_to_o')
q_to_s = OptionNode('q_to_s')
q_to_r = OptionNode('q_to_r')
t_to_z = OptionNode('t_to_z')
t_to_v = OptionNode('t_to_v')
t_to_u = OptionNode('t_to_v')
w_to_z = OptionNode('w_to_z')
w_to_x = OptionNode('w_to_x')
y_to_z = OptionNode('y_to_z')

# Create binary tree
options.add_children(a_to_m,n_to_z)
a_to_m.add_children(a_to_f,g_to_m)
a_to_f.add_children(a_to_c,d_to_f)
a_to_c.add_children(a,b_to_c)
b_to_c.add_children(b,c)
d_to_f.add_children(d,e_to_f)
e_to_f.add_children(e,f)
g_to_m.add_children(g_to_i,j_to_m)
g_to_i.add_children(g_to_h,i)
g_to_h.add_children(g,h)
j_to_m.add_children(j_to_k,l_to_m)
j_to_k.add_children(j,k)
l_to_m.add_children(l,m)
n_to_z.add_children(n_to_s,t_to_z)
n_to_s.add_children(n_to_p,q_to_s)
n_to_p.add_children(n_to_o,p)
n_to_o.add_children(n,o)
q_to_s.add_children(q_to_r,s)
q_to_r.add_children(q,r)
t_to_z.add_children(t_to_v,w_to_z)
t_to_v.add_children(t_to_u,v)
t_to_u.add_children(t,u)
w_to_z.add_children(w_to_x,y_to_z)
w_to_x.add_children(w,x)
y_to_z.add_children(y,z)

def command(cmd_string):
	if cmd_string == 'quit':
		quit()
	elif cmd_string == 'refresh':
		process_selection()

current_option = options
gui_msg = ''

def process_selection():
	global current_option
	gui_msg = topic_gui
	if len(current_option.children) == 0:
		push.send_string(topic_audio+' '+current_option.content)
		current_option = options
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