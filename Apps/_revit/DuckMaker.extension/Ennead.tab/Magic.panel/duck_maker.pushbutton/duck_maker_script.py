#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Make a new button in EnneadTab. What would I do without you."
__title__ = "Duck\nMaker"
__context__ = "zero-doc"

import os
import shutil
try:
    from pyrevit import forms
    from pyrevit.loader import sessionmgr
    IS_PYREVIT = True
except ImportError:
    import tkinter as tk
    from tkinter import filedialog
    IS_PYREVIT = False
    

def create_new_button():
    if IS_PYREVIT:
        # get new button name
        func_name = forms.ask_for_string(default = "New_Button_Name", 
                                        prompt = "Type in the name for new script",
                                        title="You are going to change the world...")
    else:
        func_name = input("Type in the name for new script:")

    func_name = func_name.replace(" ", "_").lower()

    if IS_PYREVIT:
        # pick folder location
        folder = forms.pick_folder(title = "New script location of container pushbutton", owner = None)#not sure what is owner
    else:
        folder = filedialog.askdirectory()
    
    target_folder = "{}\\{}.pushbutton".format(folder, func_name)
    new_location = "{}\\{}_script.py".format(target_folder, func_name)


    # copy from template to address
    # secure folder first
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    template_folder = "{}\\NAME_OF_THE_BUTTON.BUTTONEXTENSION".format(os.path.dirname(__file__))
    
    for file in os.listdir(template_folder):
        # print(os.path.join(template_folder, file))
        shutil.copyfile(os.path.join(template_folder, file), os.path.join(target_folder, file))
        if "_script" in file:
            new_file_name = file.replace("NAME_OF_THE_BUTTON", func_name)
            os.rename(os.path.join(target_folder, file), os.path.join(target_folder, new_file_name))

    # edit main func name
    with open(new_location) as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:

        line = line.replace('PRETTY_NAME', pretty_name(func_name))
        line = line.replace('NAME_OF_THE_BUTTON', func_name)
        new_lines.append(line)

    with open(new_location, "w") as f:
        f.write("".join(new_lines))

    #open lib on the side

    os.startfile(new_location)



def pretty_name(name):
    words = name.split('_')
    pretty_name = ' '.join(word.title() for word in words)
    return pretty_name
    
################## main code below #####################



if __name__ == "__main__":
    create_new_button()
    if IS_PYREVIT:
        sessionmgr.reload_pyrevit()
