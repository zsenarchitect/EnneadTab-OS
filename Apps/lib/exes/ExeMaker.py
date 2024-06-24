import os
import json
import shutil
import subprocess

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)) + "\\EnneadTab")

# the downloader shall read where to url based on configure file so if I re path it can update. 
# most of exe can use this logic to avoid asset folder. the configure file title can be the same as maker file


from ENVIRONMENT import EXE_ROOT_FOLDER, ROOT
EXE_PRODUCT_FOLDER = os.path.join(EXE_ROOT_FOLDER, "products")
EXE_MAKER_FOLDER = os.path.join(EXE_ROOT_FOLDER,"maker data")
EXE_SOURCE_CODE_FOLDER = os.path.join(EXE_ROOT_FOLDER,"source code")


def move_exes():
    src_folder = "{}\\dist".format(ROOT)
       
    # Copy all items from src_folder to dest_folder
    for item in os.listdir(src_folder):
        src_item = os.path.join(src_folder, item)
        dest_item = os.path.join(EXE_PRODUCT_FOLDER, item)
        
        if os.path.isdir(src_item):
            shutil.copytree(src_item, dest_item)
        else:
            shutil.copy2(src_item, dest_item)
    
    # Delete the original folder and its contents
    shutil.rmtree(src_folder)

def make_exe(maker_json):
 
    # Parse the JSON configuration
    with open(maker_json, "r") as f:
        json_config = json.load(f)
    

        # Convert JSON to command
        command = json_to_command(json_config)

        # Run the command
        subprocess.run(command)

        
def json_to_command(json_config):
    command = ['pyinstaller']
    
    for option in json_config['pyinstallerOptions']:
        if option["optionDest"] == "filenames":
            final_path = option["value"]
            continue

        if option["optionDest"] == "icon_file":
            command.append("--{}".format("icon"))
            command.append("{}".format(option['value']))
            continue
        
        if option["optionDest"] == "console":
            if option['value'] is True:
                command.append("--{}".format("console"))
            else:
                command.append("--{}".format("windowed"))
            continue
        
        if option['value'] is True:
            command.append("--{}".format(option['optionDest']))
        elif option['value'] is not False:
            command.append("--{}".format(option['optionDest']))
            command.append("{}".format(option['value']))

    command.append(final_path)
    print("\033[92m{}\033[00m".format(command))
    print ("\n\n")
    return command

def update_all_exes():
    for file in os.listdir(EXE_MAKER_FOLDER):
        if file.endswith(".json"):
            print("\033[94m{}\033[00m".format(file))
            make_exe(os.path.join(EXE_MAKER_FOLDER,file))
            print ("\n\n\n")


    move_exes()
    print ("done exe creation")
    


if __name__ == "__main__":
    update_all_exes()