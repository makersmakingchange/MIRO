fout = open('eyebrows1.csv','w')
with open('20170326_110635.txt','r') as fin:
	for line in fin:
		if 'face' in line:
			parts = line.split()
			try:
				data = parts[3].split(',')
				assert len(data) == 6
				output = parts[0]+','+parts[3]
				print(output)
				fout.write(output)
			except Exception:
				pass
		'''
		if 'wface text' in line:
			parts = line.split()
			data = parts[3].split(',')
			output = data[0]+','+data[1]+','+data[2]+'\n'
			print(output)
			fout.write(output)
		'''