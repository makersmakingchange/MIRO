from wtfj import*
import split
from os import system
'''Translation table must be updated in both tkpiece and text'''
translation_table = {
	'com': ',',
	'spc': ' ',
	'num': '#'
}

class Text(Piece):

		def _BEFORE_start(self):
			self.subscribe(Uid.ENGINE)
			self.subscribe(Uid.BLINK)
			self._text_buffer = ''
			self.filename = '../output/book2.txt'
			self._edit_mode = False
			self.i = 0
			self._edit_buffer = ''
			self._file_buffer = ''
			self._sentence_num = -1
			self.choices = [' ','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
			self.menu_options = ['#menu','#keyboard','#delete','#clear','#save','#review']
			self._ignore = ['#configure','#plus','#minus','#numkeys','#colorscheme','#blackwhiteyellow','#blackbluegreen']

		def _contains(self,upper_left, bottom_right):
			'''Helper function to determine if a shape contains the last
			eyetracker coordinates.'''
			# Until screen size is dynamic on eyetracker:
			ul = (float(upper_left[0])*1280,float(upper_left[1])*720)
			br = (float(bottom_right[0])*1280,float(bottom_right[1])*720)
			if (ul[0] < self._last_eye[0] and ul[1] < self._last_eye[1] and br[0] > self._last_eye[0] and br[1] > self._last_eye[1]):
				return True
			return False

		def _ON_blink_select(self,data):
			'''When a blink select signal is emitted, check if the last
			eye coordinate was within any of the keys'''
			shapes = self.shape_list.split(",")
			for index in range(0,len(shapes)/5):
				ul = (shapes[5*index+1],shapes[5*index+2])
				br = (shapes[5*index+3],shapes[5*index+4])
				if (self._contains(ul,br) == True):
					self.send_to(Uid.ENGINE,Msg.SELECT,str(index))
					return

		def _ON_engine_chose(self,data):
			'''Receive currently chosen letter'''
			try:
				data = translation_table[data]
			except KeyError:
				pass

			if(data in self._ignore):
				pass
			elif data!= None and str(self._edit_mode) == 'True' and data not in self.menu_options:
				self._edit_buffer = self._edit_buffer + data

			elif data not in self.menu_options:
				self._text_buffer = self._text_buffer + data
				self.send(Msg.BUFFER,self._text_buffer)
			else:
				if data in self.menu_options:
					if data == '#delete':
						self._text_buffer = list(self._text_buffer)
						self._text_buffer[-1] = ''
						self._text_buffer = ''.join(self._text_buffer)
						self.send(Msg.BUFFER,self._text_buffer)
					elif data == '#clear':
						self._text_buffer = ''
						self.send(Msg.BUFFER,self._text_buffer)
					elif data == '#save':
						if self._edit_mode == False:
							with open(self.filename, 'a+') as f:
								self._text_buffer = self._text_buffer
								f.write(self._text_buffer)
								f.close()
							self._text_buffer = ''
							self.send(Msg.BUFFER,self._text_buffer)
						if self._edit_mode == True :
							self._file_buffer[self.i] = str(self._edit_buffer)
							self._file_buffer = ' '.join(self._file_buffer)
							self.send(Msg.TEXT,'the new changed text buffer is '+ str(self._file_buffer))				
							self.send(Msg.TEXT,'The edit buffer has '+ self._edit_buffer)
							with open(self.filename, 'w') as f:
								if self._sentence_num == -1:
									self._file_buffer = self._text_buffer+self._file_buffer
								else :
									self._file_buffer = self._text_buffer +self._file_buffer + ''.join(self.sentences[self._sentence_num+1:])
								self.send(Msg.TEXT, 'the splited sentences in file are ' + str(self.sentences))
								self.send(Msg.TEXT,'the newly changed file buffer now has contents'+ str(self._file_buffer))								
								f.seek(0)
								f.write(self._file_buffer)
								f.close()
							self._edit_mode = False
							self._text_buffer = ''
							self._edit_buffer = ''
					elif data == '#review':
						try:
							self._text_buffer = self._openFile(self._sentence_num)
						except IndexError:
							self._sentence_num = -1
							self._text_buffer = self._openFile(self._sentence_num)
						self.send(Msg.TEXT,'the last sentence in the faile is ' +str(self._text_buffer))
						self.send(Msg.BUFFER,self._text_buffer)
						self._sentence_num = self._sentence_num - 1
				else:
					self._text_buffer = self._text_buffer + data
					self.send(Msg.BUFFER,self._text_buffer)


		def _ON_engine_edit(self,data):
			'''This function operates when user wants to edit what he/she has typed out in the file '''
			if data == 'True':
				self._edit_mode = True
				self._file_buffer=self._openFile(self._sentence_num)
				self.send(Msg.TEXT,'the last sentence entered is '+ str(self._file_buffer))
				self._length = len(self._file_buffer)
				self.i = 0
				self._file_buffer = self._file_buffer.split()
				self.send_to(Uid.TKPIECE,Msg.TEXT,'feedback,'+self._file_buffer[self.i])
				self.send_to(Msg.TEXT,'THE edit mode is ' + str(self._edit_mode))
			if data == 'select0':
				self._file_buffer[self.i] = ''
				self.send(Msg.TEXT,'the new string is '+ str(self._file_buffer))
			elif data == 'select1' and self.i < self._length :
				self.i = self.i+1
				self.send_to(Uid.TKPIECE,Msg.TEXT,'feedback,'+self._file_buffer[self.i])

		def _openFile(self,_sentence_num):
			f = open(self.filename,'r')
			for line in f :
				self.sentences  = split.split_into_sentences(line)
				'store all previous text'
				self._text_buffer  = ''.join(self.sentences[0:_sentence_num])
				'give back last sentences'
				last_sentence  = self.sentences[_sentence_num]
				#self._text_buffer = self._text_buffer + (sentences[-1])
			#print( 'text_buffer has '+str(self._text_buffer))
			return str(last_sentence)
				



		@staticmethod
		def script():
  					text_entry = [

								'@text marco',
								'engine chose #review',
								#'engine chose #review',
								#'engine chose #review',
								#'engine chose #review',
								#'engine chose #review',
								#'engine chose #review',
								#'engine chose H',
								#'engine chose a',
								#'engine chose r',
								#'engine chose v',
								#'engine chose e',
								#'engine chose y',
								#'engine chose  ',
								#'engine chose J',
								#'engine chose i',
								#'engine chose a',
								#'engine chose n',
								#'engine chose #clear',
								#'engine chose 1',
								#'engine chose .',
								#'engine chose com',
								#'engine chose spc',
								#'engine chose num',
								#'engine chose #clear',
								#'engine chose  ',
								#'engine chose J',
								#'engine chose i',
								#'engine chose a',
								#'engine chose n',
								#'engine chose #undo',
								#'engine chose #commit',
								#'engine chose g',
								#'engine edit True',
								#'engine edit select1',
								#'engine edit select0',
								#'engine chose were',
								#'engine chose #save',
								'engine edit True',
								#'engine openFile',
								#'engine edit select0',
								#'engine chose A',
								#'engine chose B',
								#'engine chose  ',
								'engine edit select1',
								'engine edit select0',
								'engine chose a',
								'engine chose a',
								'engine chose s',
								'engine chose t',
								#'engine edit select0',
								#'engine chose Tmrw',
								'engine chose #save',
								#'engine edit previous',
								#'engine edit select0',
								#'engine chose Hello',
								#'engine chose #save',
								#'engine edit previous',
								#'engine edit select1',
								#'engine edit select0',
								#'engine chose was',
								#'engine chose #save',
								#'engine chose #commit',
								#'engine save True',
								#'engine chose Hi',
								#'engine commit True',
								#'engine save True',
								#'engine chose A',
								#'engine chose B',
								#'engine commit True',
								'@text stop'

						]
					return Script(text_entry)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Text,argv)
