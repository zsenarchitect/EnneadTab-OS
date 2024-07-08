
#  create a .bat file that run above command and save it to cuurent folder
"""NOT IN  USE"""
import os


def create_bat():
   

    batch_commands = "pyrevit extend ui EnneadTab https://github.com/zsenarchitect/EnneadTab.git"


    # create a bat file on the desktop
    file_path = os.path.join(os.path.expanduser("~"), "Desktop", "EnneadTab.bat")

    # Create the .bat file and write the batch commands to it
    with open(file_path, 'w') as file:
        file.write(batch_commands)




if __name__ == "__main__":
    create_bat()