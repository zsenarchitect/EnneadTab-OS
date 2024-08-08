#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "capitalize_data"

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
def capitalize_data():

    t = DB.Transaction(doc, __title__)
    t.Start()
    areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    for area in areas:
        para = area.LookupParameter("Sub-Section Name")

        if para:
            current_value = para.AsString()
            if current_value:
                para.Set(current_value.upper())


        para = area.LookupParameter("Name")
        if para:
            current_value = para.AsString()
            if current_value:
                para.Set(current_value.upper())
    t.Commit()

################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    capitalize_data()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







