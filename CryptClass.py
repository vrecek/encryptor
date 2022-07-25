import binascii
from genericpath import isdir
import os
from cryptography.fernet import Fernet


class CryptClass():
   key: bytes
   fileSkip: list[str]

   def __init__(self, loopFileSkip: list[str]) -> None:
      self.key = b''
      self.fileSkip = loopFileSkip
      


   def createRequiredFiles(self) -> None:
      path = os.path.join(os.getcwd(), 'info')

      if not os.path.exists(path):
         os.mkdir(path)

         self.writeFile('info/key.txt', '', False)
         self.writeFile('info/encryptedFiles.txt', '', False)



   def fileLoopSkip(self, file: str) -> bool:
      return True if file in self.fileSkip else False



   def getContent(self, file: str, returnAsHex: bool = False) -> bytes:
      with open(file, 'rb') as openFile:
         content = openFile.read()

         return binascii.hexlify(content) if returnAsHex else content



   def checkExtensions(self, file: str) -> list[bool, bool, bool, bool]:
      isDir = isdir(file)
      isImage = file.endswith(('.png', '.jpg', '.jpeg'))
      isTxt = file.endswith('.txt')

      canEncrypt = isDir or isImage or isTxt
      
      return [isDir, isImage, isTxt, canEncrypt]



   def decryptedFileRemove(self, decryptedFiles: tuple[str]) -> None:
      files = (
         'info/encryptedFiles.txt',
         'info/key.txt'
      )

      content = self.getContent(files[0]).decode('utf-8').split()


      for word in decryptedFiles:
         if word in content:
            content.remove(word)


      if len(content) == 0:
         for delFile in files:
            os.remove(delFile)

         os.rmdir('info')

      else:
         self.writeFile(files[0], ' '.join(content), False)



   def writeFile(self, fileName: str, content: str | bytes, append: bool) -> None:
      contentType = '' if type(content) is str else 'b'

      if append:
         writeType = 'a'
         writeContent = f'{ content } '
      else:
         writeType = 'w'
         writeContent = content

      openType = f'{ writeType }{ contentType }'

      with open(fileName, openType) as openFile:
         openFile.write(writeContent)



   def returnFernet(self, key: bytes = None) -> Fernet:
      genKey = key if key else Fernet.generate_key()
      self.key = genKey

      return Fernet(genKey)



   def checkRequiredFilesExist(self) -> None:
      path = os.path.join(os.getcwd(), 'info')


      if not os.path.exists(path):
         raise('No "info" directory found. Start encryption first.')


      req_files = ('encryptedFiles.txt', 'key.txt')
      current_dir = os.listdir(path)

      for file in req_files:
         if not file in current_dir:
            raise('No required files found. Start encryption first.')
         


   def getKey(self) -> bytes:
      return self.key
