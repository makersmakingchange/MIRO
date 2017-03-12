from wtfj import*

class Text(Piece):

    def _BEFORE_start(self):
                self.subscribe(Uid.ENGINE)
                self._text_buffer = ''
                self.filename = 'book2.txt'

    def _ON_engine_chose(self,data):
                '''Receive currently chosen letter'''
                self._text_buffer = self._text_buffer + data

    def _ON_engine_commit(self,data):
                '''Receive a boolean variable.If evaluated to be true, this function will
                save the contents in buffer in a file '''
                if data == 'True' :
                        with open(self.filename, 'a+') as f:
                                self._text_buffer = self._text_buffer + '\n'
                                f.write(self._text_buffer)
                                f.close()
                        self.send(Msg.TEXT,'User has just typed '+ self._text_buffer)
                        self.send_to(Uid.TKPIECE,Msg.TEXT,'feedback,'+self._text_buffer)

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
                 'engine commit True',
                '@text stop'

            ]
            return Script(text_entry)

if __name__ == '__main__':
	from sys import argv
	Runner.run_w_cmd_args(Text,argv)
