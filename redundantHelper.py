from typing import Callable
from CryptClass import CryptClass
import os

DEFAULT_DIR = os.getcwd()
SKIP_WORDS = ('encryption.py', 'decryption.py', 'CryptClass.py', 'info', '__pycache__', 'redundantHelper.py', '.git', '.gitignore', 'README.md')

def mainLogic(crypt: CryptClass, file: str, initFunc: Callable[[str], None], actionFunc: Callable[[str, bool, bool], None]):
   if crypt.fileLoopSkip(file): return

   [isDir, isImage, isTxt, canEncrypt] = crypt.checkExtensions(file)


   if not canEncrypt:
      return

   
   if isDir:
      directoryFiles = os.listdir(file)

      os.chdir( os.path.join(os.getcwd(), file) )
      
      for innerFile in directoryFiles:
         initFunc(innerFile)

      return


   actionFunc(file, isImage, isTxt)