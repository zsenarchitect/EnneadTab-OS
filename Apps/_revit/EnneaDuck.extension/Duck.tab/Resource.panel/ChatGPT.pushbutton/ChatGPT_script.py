#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Fire UP ChatGPT in Revit.\n\nIt can answer any questions you might have."
__title__ = "ChatGPT"
__context__ = 'zero-doc'
__youtube__ = "https://youtu.be/NoJmQ7GFzMs"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=29655"
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #

from EnneadTab import ENVIRONMENT, MODULE_HELPER

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def ChatGPT():
    #C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\Utility.panel\exe_2.stack\chatGPT.pushbutton\chatGPT_script.py
    module_path = "{}\ENNEAD.extension\Ennead.tab\Utility.panel\exe_2.stack\chatGPT.pushbutton\chatGPT_script.py".format(ENVIRONMENT.get_EnneadTab_For_Revit_root())
    func_name = "main"
    MODULE_HELPER.run_func_in_module(module_path, func_name)


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    ChatGPT()
    
