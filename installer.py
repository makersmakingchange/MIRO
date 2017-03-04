appending = "\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
import os
cwd_parts = os.getcwd().split('\\')
assert cwd_parts[1] == 'Users'
d = cwd_parts[0]+'\\'+cwd_parts[1]+'\\'+cwd_parts[2]+appending
with open(d+'\\test2.txt','w') as f: f.write('YES\n')