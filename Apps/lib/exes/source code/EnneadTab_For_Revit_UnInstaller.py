import configparser
import os
import time
import _Exe_Util

@_Exe_Util.try_catch_error
def main():
    # Get the current user's profile directory
    user_profile = os.path.expanduser("~")

    # Path to the .ini file
    file_path = os.path.join(user_profile, 'AppData', 'Roaming', 'pyRevit', 'pyRevit_config.ini')
    if not os.path.exists(file_path):
        print("Are you sure pyRevit has been installed?")
        print ("Close this window and check again.")
        return

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the .ini file
    config.read(file_path)

    # Construct the new path for userextensions
    new_userextensions_path = os.path.join(_Exe_Util.ESOSYSTEM_FOLDER, 'EA_Dist', 'Apps', '_revit')

    # Modify the necessary items in the [...] section
    if 'core' in config:
        config.set('core', 'userextensions', '[]')
        config.set('core', 'colorize_docs', 'true')

    if 'tabcoloring' in config:
        config.set('tabcoloring', 'tabstyle_index', '3')
        config.set('tabcoloring', 'family_tabstyle_index', '8')

    # Write the changes back to the .ini file
    with open(file_path, 'w') as configfile:
        config.write(configfile)

    print("EnneadTab for Revit has been attached to pyRevit.")
    print ("You can now close this window and open Revit.")



if __name__ == "__main__":
    main()
    time.sleep(30)