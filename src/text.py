from wtfj import*

class Text(Piece):

		def _BEFORE_start(self):
			self.subscribe(Uid.ENGINE)
			self.subscribe(Uid.BLINK)
			self._text_buffer = ''
			self.filename = '../output/book2.txt'
			self._edit_mode = False
			self.i = 0
			self._edit_buffer = ''

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
			if data!= None and str(self._edit_mode) == 'True':
				self._edit_buffer = self._edit_buffer + data
				#self.send(Msg.TEXT,'the editor buffer has', + self._edit_buffer)
			else:
				self._text_buffer = self._text_buffer + data
				self.send(Msg.BUFFER,self._text_buffer)


		def _ON_engine_commit(self,data):
			'''Receive a boolean variable.If evaluated to be true, this function will
			save the contents in buffer in a file '''
			if data == 'True' and self._edit_mode == False :
					self.send(Msg.TEXT,'User has just commited '+ self._text_buffer)
			if self._edit_mode == True :
					self.send(Msg.TEXT,'The edit buffer has '+ self._edit_buffer)
					self._text_buffer[self.i] = str(self._edit_buffer)
					self._text_buffer = ''.join(self._text_buffer)
					self.send(Msg.TEXT,'the new changed text buffer is '+ self._text_buffer)
					self._edit_mode = False
					
		
		def _ON_engine_save(self,data):
			if data == 'True':
				self.send(Msg.TEXT,'saving file')
				self.send(Msg.TEXT,'the file will save the text buffer which is ' + self._text_buffer)
				with open(self.filename, 'a+') as f:
					self._text_buffer = self._text_buffer
					f.write(self._text_buffer)
					f.close()
				self._text_buffer = ''

		def _ON_engine_edit(self,data):
			'''This function operates when user wants to see what he/she has typed out '''
			if data == 'True':
				self._edit_mode = True
				self.length = len(self._text_buffer)
				self.i = 0
				self._text_buffer = self._text_buffer.split()
				self.send_to(Uid.TKPIECE,Msg.TEXT,'feedback,'+self._text_buffer[self.i])
				self.send_to(Msg.TEXT,'THE edit mode is ' + str(self._edit_mode))
			if data == 'select0':
				self._text_buffer[self.i] = ''
				self.send(Msg.TEXT,'the new string is '+ str(self._text_buffer))
			elif data == 'select1' and self.i < self.length :
				self.i = self.i+1
				self.send_to(Uid.TKPIECE,Msg.TEXT,'feedback,'+self._text_buffer[self.i])
			
				



		@staticmethod
		def script():
  					text_entry = [
								'@text marco',
								'engine chose H',
								'engine chose a',
								'engine chose r',
								'engine chose v',
								'engine chose e',
								'engine chose y',
								'engine chose  ',
								'engine chose J',
								'engine chose i',
								'engine chose a',
								'engine chose n',
								'engine chose g',
								'engine commit True',
								'engine edit True',
								'engine edit select0',
								'engine chose A',
								'engine chose B',
								'engine chose  ',
								'engine commit True',
								'engine save True',
								'engine chose Hi',
								'engine commit True',
								'engine save True',
								'@text stop'

						]
					return Script(text_entry)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Text,argv)

