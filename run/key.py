from pynput.keyboard import Listener
import logging



def onpress(key):
	pass
	#print(str(key))
	#logging.info(key)



#logging.basicConfig(
#	filename=('file.txt'),
#	format='%(asctime)s: %(message)s',
#	level=logging.DEBUG
#)


with Listener(on_press=onpress) as listener:
	listener.join()
