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
			self._sentence_num = 0
			self.choices = [' ','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
			self.menu_options = ['#menu','#keyboard','#delete','#clear','#save','#review','#speak']
			self._ignore = ['#configure','#plus','#minus','#numkeys','#colorscheme','#blackwhiteyellow','#blackbluegreen']

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
					elif data == '#speak':
						self.send_to(Uid.AUDIO,Req.SPEAK,self._text_buffer)
					elif data == '#clear':
						self._text_buffer = ''
						self.send(Msg.BUFFER,self._text_buffer)
					elif data == '#save':
						if self._edit_mode == False:
							if '.' not in self._text_buffer :
								self._text_buffer += '.'
							with open(self.filename, 'a+') as f:
								self._text_buffer = self._text_buffer
								f.write(self._text_buffer)
								f.close()
							self._text_buffer = ''
							self.send(Msg.BUFFER,self._text_buffer)
						if self._edit_mode == True :
							
							if self.i==self._length-1:
								self._edit_buffer = list(self._edit_buffer)
								self._edit_buffer += ' '
								self._edit_buffer = ''.join(self._edit_buffer)
							else :
								self._edit_buffer = self._edit_buffer
							self._file_buffer[self.i] = str(self._edit_buffer)
							self._file_buffer = ' '.join(self._file_buffer)
								
							if '.' not in str(self._file_buffer) and self.i==self._length-1:
								self._file_buffer= self._file_buffer.split(' ')
								self._file_buffer[-2] += '.'
								self._file_buffer=' '.join(self._file_buffer)
							with open(self.filename, 'w') as f:
								if self._sentence_num == -1:
									self._file_buffer = self._text_buffer +' '+ self._file_buffer
								else :
									self._file_buffer = self._text_buffer +self._file_buffer +' '+ ''.join(self.sentences[self._sentence_num+1:])								
								f.seek(0)
								f.write(self._file_buffer)
								f.close()
							self._edit_mode = False
							self._text_buffer = ''
							self._edit_buffer = ''
					elif data == '#review':
						try:
							self._sentence_num = self._sentence_num - 1
							self._text_buffer = self._openFile(self._sentence_num)
						except IndexError:
							self._sentence_num = -1
							self._text_buffer = self._openFile(self._sentence_num)
						self.send(Msg.BUFFER,self._text_buffer)
				else:
					self._text_buffer = self._text_buffer + data
					self.send(Msg.BUFFER,self._text_buffer)


		def _ON_engine_edit(self,data):
			'''This function operates when user wants to edit what he/she has typed out in the file '''
			if data == 'True':
				self._edit_mode = True
				self._file_buffer=self._openFile(self._sentence_num)	
				self.send(Msg.TEXT,'the last sentence entered is '+ ','.join(self._file_buffer.split()))
				self.send(Msg.BUFFER,self._file_buffer.split())
				self._length = len(self._file_buffer.split())
				self.i = 0
				self._file_buffer = self._file_buffer.split()
				self.send_to(Uid.TKPIECE,Msg.TEXT,'feedback,'+self._file_buffer[self.i])
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
				#self.send(Msg.TEXT,'The sentences in the file are' + str(self.sentences))
				'store all previous text'
				self._text_buffer  = ' '.join(self.sentences[0:_sentence_num])
				'give back last sentences'
				last_sentence  = self.sentences[_sentence_num]

			return str(last_sentence)
				



		@staticmethod
		def script():
  					text_entry = [

								'@text marco',
								#'engine chose a',
								#'engine chose .',
								#'engine chose #save',
								'engine chose #review',
								'engine chose #review',
								#'engine edit True',
								#'engine edit select1',
								#'engine edit select1',
								#'engine edit select0',
								#'engine chose me',
								#'engine chose #save',
								'@text stop'

						]
					return Script(text_entry)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Text,argv)
