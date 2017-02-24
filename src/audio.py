import winsound
import zmq

# Constants and stable vars
AUDIO_PATH = '../res/audio/'
SOCKET_SUB = 'tcp://localhost:5556'
topic_filter = '@audio'

# Create subscriber socket
context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect(SOCKET_SUB)

if isinstance(topic_filter, bytes):
    topic_filter = topic_filter.decode('ascii')
sub.setsockopt_string(zmq.SUBSCRIBE,topic_filter)

def speak_character(character):
	if character == 'a:m':
		winsound.PlaySound(AUDIO_PATH+'a_to_m_sound.wav',winsound.SND_FILENAME)
	elif character == 'n:z':
		winsound.PlaySound(AUDIO_PATH+'n_to_z_sound.wav',winsound.SND_FILENAME)
	elif character in 'abcdefghijklmnopqrstuvwxyz':
		winsound.PlaySound(AUDIO_PATH+character+'_sound.wav',winsound.SND_FILENAME)
	elif character == '{}':
		winsound.PlaySound(AUDIO_PATH+'space_sound.wav',winsound.SND_FILENAME)
	elif character == '<':
		winsound.PlaySound(AUDIO_PATH+'undo_sound.wav',winsound.SND_FILENAME)

while True:  
    string = sub.recv_string()
    if 'cmd=quit' in string:
    	quit()
    else:
		speak_character(string.split()[1])
		
