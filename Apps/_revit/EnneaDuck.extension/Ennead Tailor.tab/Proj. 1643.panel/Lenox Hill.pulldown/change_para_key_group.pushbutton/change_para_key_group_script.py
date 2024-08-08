#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "change_para_key_group"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error
def change_para_key_group():
    sample_area = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).FirstElement()

    for para in sample_area.Parameters:
        if "LifeSafetyKey" == para.Definition.Name:
            break

    para_defintion = para.Definition
    print (para_defintion.ParameterGroup)
        


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    change_para_key_group()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







