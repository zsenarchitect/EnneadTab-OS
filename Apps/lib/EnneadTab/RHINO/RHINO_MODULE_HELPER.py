#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import imp
import random

import sys
sys.path.append(os.path.dirname(__file__))
import FOLDER
import ENVIRONMENT
import ERROR_HANDLE
import NOTIFICATION
import VERSION_CONTROL
import LOG


def run_Rhino_button(locator, *args):
    """Run a specified function in a specified file, for use with Rhino buttons.

    Args:
        folder (str): The folder name for the button script, in EnneadTab sources codes folder.
        file_name (str): The file name for the button script, without the .py extension.
        func_name (str): The function name to run in the button script. To run entire script, use "file_name".
        *args: Positional arguments to pass to the function.
    """


    root = ENVIRONMENT.RHINO_FOLDER
    module_path = "{}\\{}".format(root, locator)


    # this is to handle only one senario---the speciall installer rui folder structure
    if not os.path.exists(module_path):
        module_path = "{}\\RHINO\\{}".format(ENVIRONMENT.CORE_FOLDER, locator)
    
    # add the folder of the module to the system path for referencing additional modules
    module_folder = os.path.dirname(module_path)
    if module_folder not in sys.path:
        sys.path.append(module_folder)

    head, tail = os.path.split(module_path)
    func_name = tail.replace(".py", "")
    module_name = FOLDER.get_file_name_from_path(module_path).replace(".py", "")
    ref_module = imp.load_source(module_name, module_path)

    
    func = getattr(ref_module, func_name, None)
    if func is None:
        for surfix in ["_left", "_right"]:
            func = getattr(ref_module, func_name.replace(surfix, ""), None)
            if func is not None:
                break
        else:
            NOTIFICATION.messenger(main_text="Oooops, cannot find the func <{}> in source code.\nContact SZ and let him know. Thx!".format(func_name))
            return

    @LOG.log(module_path, func_name)
    @ERROR_HANDLE.try_catch_error()
    def runner(*args):
        func(*args)

    runner()

    
    if random.random() < 0.3:
        VERSION_CONTROL.update_EA_dist()