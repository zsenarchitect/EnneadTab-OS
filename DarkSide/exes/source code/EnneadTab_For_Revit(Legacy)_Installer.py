import configparser
import os
import time
import psutil
import _Exe_Util

def check_revit_running():
    # Check if Revit is running (case-insensitive)
    for process in psutil.process_iter(['pid', 'name']):
        if 'revit' in process.info['name'].lower():
            return True
    return False

@_Exe_Util.try_catch_error
def main():
    if not _Exe_Util.is_avd() and check_revit_running():
        print("Please close all running instances of Revit before making change to EnneadTab Revit.")
        return
    # Get the current user's profile directory
    user_profile = os.path.expanduser("~")

    # Path to the .ini file
    file_path = os.path.join(user_profile, 'AppData', 'Roaming', 'pyRevit', 'pyRevit_config.ini')
    if not os.path.exists(file_path):
        print("Are you sure pyRevit has been installed?")
        print("Close this window and check again.")
        return

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the .ini file
    config.read(file_path)

    # Construct the new path for userextensions
    # new_userextensions_path = os.path.join(_Exe_Util.ESOSYSTEM_FOLDER, 'EA_Dist', '_revit')
    new_userextensions_path = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published_Beta_Version"

    # Modify the necessary items in the [...] section
    if 'core' in config:
        config.set('core', 'userextensions', '["{}"]'.format(new_userextensions_path))
        config.set('core', 'colorize_docs', 'true')

    if 'tabcoloring' in config:
        config.set('tabcoloring', 'tabstyle_index', '3')
        config.set('tabcoloring', 'family_tabstyle_index', '8')

    # Write the changes back to the .ini file
    with open(file_path, 'w') as configfile:
        config.write(configfile)

    print("EnneadTab-for-Revit(Legacy) has been attached to pyRevit.")
    print ("You can now close this window and open Revit.")



if __name__ == "__main__":
    main()
    time.sleep(30)