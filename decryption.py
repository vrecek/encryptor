import binascii
from CryptClass import CryptClass
import os
from redundantHelper import SKIP_WORDS, DEFAULT_DIR, mainLogic

crypt = CryptClass(loopFileSkip = SKIP_WORDS)
crypt.checkRequiredFilesExist()
fernet = crypt.returnFernet(crypt.getContent('info/key.txt'))

dirFiles = os.listdir()
decrypted_files = []



def decryptFile(file: str, isImage: bool, isTxt: bool) -> None:
   content = crypt.getContent(file)
   decrypted = fernet.decrypt(content)

   if isImage:
      decrypted = binascii.unhexlify(decrypted)

   crypt.writeFile(file, decrypted, False)
   decrypted_files.append(file)



def init(file: str) -> None:
   mainLogic(crypt, file, init, decryptFile)



for file in dirFiles:
   init(file)

   os.chdir(DEFAULT_DIR)



crypt.decryptedFileRemove(decrypted_files)

