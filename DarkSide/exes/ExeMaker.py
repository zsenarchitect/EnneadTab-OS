import os
import json
import shutil
import subprocess
import traceback
import sys
import time
import re


# print("Python executable:", sys.executable)
# print("Python version:", sys.version)
# print("sys.path:", sys.path)
# print("Environment variables:", os.environ)


# this will disable all pygame talk
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"



sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "\\Apps\\lib\\EnneadTab")

from ENVIRONMENT import ROOT, EXE_PRODUCT_FOLDER  # pyright: ignore
import NOTIFICATION  # pyright: ignore



DARKSIDE_FOLDER = os.path.dirname(os.path.dirname(__file__))

EXE_FOLDER = os.path.join(DARKSIDE_FOLDER, "exes")
EXE_MAKER_FOLDER = os.path.join(EXE_FOLDER, "maker data")
EXE_SOURCE_CODE_FOLDER = os.path.join(EXE_FOLDER,"source code")
TEMP_SPEC_FOLDER = os.path.join(EXE_FOLDER, "temp_specs")

PYGAME_ALLOWS = ["Speaker.sexyDuck",
                 "LastSyncMonitor.sexyDuck"]




class NoGoodSetupException(Exception):
    def __init__(self):
        super().__init__("The setup is not complete or you are working on a new computer.")
        

PY_INSTALLER_LOCATION = "pyinstaller"

# try:
#     import pyinstaller
#       # Default location if import works
# except ModuleNotFoundError:
#     # Some computers cannot set up venv due to permission, so pyinstaller has to be installed in the global site packages.
#     possible_pyinstaller_locations = [
#         "C:\\Users\\szhang\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python310\\Scripts\\pyinstaller.exe"
#         "C:\\Users\\szhang\\Documents\\pyenv\\pyenv-win\\shims\\pyinstaller.bat"
#     ]
#     for location in possible_pyinstaller_locations:
#         if os.path.exists(location):
#             print("additional pyinstaller found")
#             PY_INSTALLER_LOCATION = location
#             break
#     else:
#         raise NoGoodSetupException()

def move_exes():
    src_folder = "{}\\dist".format(ROOT)

    # in some setup environemt we cannot run pyinstaller propperly so no src_folder will be created.
    if not os.path.exists(src_folder):
        return
       
    # Copy all items from src_folder to dest_folder
    for item in os.listdir(src_folder):
        src_item = os.path.join(src_folder, item)
        dest_item = os.path.join(EXE_PRODUCT_FOLDER, item)
        
        attemp = 0
        while attemp < 3:
            try:
                if os.path.isdir(src_item):
                    shutil.copytree(src_item, dest_item)
                else:
                    shutil.copy2(src_item, dest_item)
                break
            except:
                time.sleep(2)
                attemp += 1
        
    # Delete the original folder and its contents
    shutil.rmtree(src_folder)

def make_exe(maker_json):
 
    # Parse the JSON configuration
    with open(maker_json, "r") as f:
        
    

        # Convert JSON to command
        command = json_to_command(f)

        try:
            # Run the command
            subprocess.run(command)
        except Exception as e:
            red_text = "\033[31m"
            reset_color = "\033[0m"
            print("{}Error updating exes: {} {}".format(red_text, traceback.format_exc(), reset_color))
           

def repath(path):
    # this is to be able to make exe from any named repo
    return path.replace("C:\\Users\\szhang\\github\\EnneadTab-OS", ROOT)
        
def json_to_command(json_file):
    json_config = json.load(json_file)
    command = [PY_INSTALLER_LOCATION]

    for option in json_config['pyinstallerOptions']:
        if option["optionDest"] == "filenames":
            final_path = option["value"]
            final_path = repath(final_path)
            continue

        if option["optionDest"] == "icon_file":
            command.append("--{}".format("icon"))
            icon_path = repath(option['value'])
            command.append(icon_path)
            continue

        if option["optionDest"] == "console":
            if option['value'] is True:
                command.append("--{}".format("console"))
            else:
                command.append("--{}".format("windowed"))
            continue

        if option["optionDest"] == "datas":
            command.append("--add-data")
            path = repath(option['value'])
            command.append(path)
            continue  

        if option['value'] is True:
            command.append("--{}".format(option['optionDest']))
        elif option['value'] is not False:
            command.append("--{}".format(option['optionDest']))
            command.append("{}".format(option['value']))

    # Add the version file for copyright information
    # version_file_path = create_version_file(final_path)
    # command.append("--version-file")
    # command.append(version_file_path)

    
    command.append("--log-level=WARN")  # disable output in terminal
    command.append(final_path)

    if os.path.basename(json_file.name) not in PYGAME_ALLOWS:
        command.append("--exclude-module")
        command.append("pygame")

    print("\033[92m{}\033[00m".format(command))
    return command

def create_version_file(final_path):
    with open(os.path.join(EXE_FOLDER, "enneadtab_spec_template.txt"), "r") as template_file:
        template = template_file.read()

    version_info = {
        "CompanyName": "Ennead Architects",
        "FileDescription": "EnneadTab Application",
        "FileVersion": "1.0.0.0",
        "InternalName": "EnneadTab",
        "LegalCopyright": "Copyright © Ennead Architects 2024",
        "OriginalFilename": os.path.basename(final_path),
        "ProductName": "EnneadTab",
        "ProductVersion": "1.0.0.0"
    }


    with open(final_path, "r") as main_py_file:
        main_py_content = main_py_file.read()
        version_info.update(parse_version_info(main_py_content))

    version_file_content = template.format(**version_info)

    if not os.path.exists(TEMP_SPEC_FOLDER):
        os.makedirs(TEMP_SPEC_FOLDER)

    version_file_path = os.path.join(TEMP_SPEC_FOLDER, "{}_version_info.txt".format(os.path.basename(final_path).replace(".py", "")))
    with open(version_file_path, "w") as version_file:
        version_file.write(version_file_content)

    return version_file_path

def parse_version_info(content):
    info = {}
    keys = ["__version__", "__description__"]
    for key in keys:
        match = re.search(r'{} = ["\']([^"\']+)["\']'.format(key), content)
        if match:
            info[key.strip("_")] = match.group(1)
    return info

def recompile_exe(single_exe = None):
    
    for file in os.listdir(EXE_MAKER_FOLDER):
        if single_exe and single_exe != file:
            continue
        if file.endswith(".sexyDuck"):
            print("\033[94m{}\033[00m".format(file))
            make_exe(os.path.join(EXE_MAKER_FOLDER,file))
            print ("\n")


    move_exes()
    print ("done exe creation")
    NOTIFICATION.messenger("Exe finish compiling")
    


if __name__ == "__main__":
    # recompile_exe()
    # recompile_exe(single_exe="RevitExportRenamer.sexyDuck")
    # recompile_exe(single_exe="Speaker.sexyDuck")
    # recompile_exe(single_exe="IndesignAccOpenner.sexyDuck")
    recompile_exe(single_exe="AccFileOpenner.sexyDuck")
    # recompile_exe(single_exe="Pdf2OrderedJpgs.sexyDuck")
    # recompile_exe(single_exe="RevitIniDeployer.sexyDuck")
    # recompile_exe(single_exe="LastSyncMonitor.sexyDuck")