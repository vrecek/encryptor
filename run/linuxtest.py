import os
import time

with open(os.path.join(os.path.expanduser('~'), 'Desktop', 'STARTLINUXSCRIPT.txt'), 'w') as file:
    file.write('test')
    time.sleep(10)