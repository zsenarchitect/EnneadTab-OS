#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Pick Name[De-Activate]"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
from Autodesk.Revit.UI.Events import SelectionChangedEventArgs
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from System import EventHandler, Uri

# get the script folder
script_folder = os.path.dirname(os.path.realpath(__file__))
pulldown_folder = os.path.dirname(script_folder)
other_script_folder = "{}\\pick_name_activate.pushbutton".format(pulldown_folder)
# print other_script_folder
import sys
sys.path.append(other_script_folder)
from pick_name_activate_script import event_handler_function
                
                
@EnneadTab.ERROR_HANDLE.try_catch_error
def pick_name_deactivate():
    __revit__.SelectionChanged -= EventHandler[SelectionChangedEventArgs](event_handler_function)      
    EnneadTab.NOTIFICATION.messenger(main_text = "Name picker Disabled.")
    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    pick_name_deactivate()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)











