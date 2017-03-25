fout = open('eyebrows1.csv','w')
with open('20170325_162429.txt','r') as fin:
	for line in fin:
		if 'wface text' in line:
			parts = line.split()
			data = parts[3].split(',')
			output = data[0]+','+data[1]+','+data[2]+'\n'
			print(output)
			fout.write(output)