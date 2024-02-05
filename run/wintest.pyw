import os
import time

with open(os.path.join(os.path.expanduser('~'), 'Desktop', 'STARTSCRIPT.txt'), 'w') as file:
    file.write('test')