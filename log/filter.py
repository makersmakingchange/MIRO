fout = open('eyebrows1.csv','w')
with open('20170311_153423.txt','r') as fin:
	for line in fin:
		if 'wface text' in line:
			parts = line.split()
			data = parts[3].split(',')
			output = parts[0]+','+data[0]+','+data[1]+'\n'
			print(output)
			fout.write(output)