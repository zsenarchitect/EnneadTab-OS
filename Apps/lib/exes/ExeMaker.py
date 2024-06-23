import os
import json
import subprocess

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)) + "\\EnneadTab")

# the downloader shall read where to url based on configure file so if I re path it can update. 
# most of exe can use this logic to avoid asset folder. the configure file title can be the same as maker file


from ENVIRONMENT import EXE_ROOT_FOLDER
EXE_PRODUCT_FOLDER = os.path.join(EXE_ROOT_FOLDER, "products")
EXE_MAKER_FOLDER = os.path.join(EXE_ROOT_FOLDER,"maker data")
EXE_SOURCE_CODE_FOLDER = os.path.join(EXE_ROOT_FOLDER,"source code")



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
        if option['value'] is True:
            command.append("--{}".format(option['optionDest']))
        elif option['value'] is not False:
            command.append("--{}".format(option['optionDest']))
            command.append("{}".format(option['value']))
    
    return command

def update_all_exes():
    for file in os.listdir(EXE_MAKER_FOLDER):
        if file.endswith(".json"):
            make_exe(os.path.join(EXE_MAKER_FOLDER,file))

    print ("done exe creation")


if __name__ == "__main__":
    update_all_exes()