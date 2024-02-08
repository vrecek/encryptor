# DISCLAIMER

This is an educational project, focused mainly on improving python skills, as well as how do systems work. <br>

I do not take any responsibility for damaging your system. Use it at your own risk. <br>

<br>

#### Encryptor/Decryptor

This is a python program that allows to encrypt/decrypt whole directories recursively. <br><br>



#### Requirements

It requires ```cryptography.fernet``` library and obviously Python3. <br> <br><br>



#### How to use

*First way:*

```python3 index.py``` -> starts in a directory, where the script was executed.

*Second way*

```python3 index.py <path>``` -> starts in a ```<path>``` directory <br> <br>


#### Details

Main class is ```CryptoApp.py```, it includes essential utils like encryption/decryption, OS detection, launching own script on startup, specifying which files should be modified, handling wallpaper etc. <br>

- Upon starting, ```.key``` file is created, that contains decryption key. Without it, you will not be able to decrypt files. After decryption, this file is automatically removed.
- When using ```CryptoApp.cronStartupAction```, ```.cron_copy``` file is created, that contains user's current crontable. After decryption, this file is automatically removed.
- This works recursively, which means it will handle EVERY file from starting point, even when starting from root directory.
- You can choose which extensions will be modified, and which files will not <br>


#### ```index.py``` example

- Get the starting path, and initialize important variables.
- Decide which files and extensions should be handled.
- Initialize ```CryptoApp```

*Encryption*

- Encrypt files
- Create cron/registry entry to start your own script on every startup
- Create JSON file that contains encryption details (os, total files, old wallpaper)
- Create some files on desktop
- Change wallpaper

*Decryption*

- Decrypt files
- Remove cron/registry entry and disable script that's currently running (linux)
- Remove previously created desktop files
- Change to original wallpaper
