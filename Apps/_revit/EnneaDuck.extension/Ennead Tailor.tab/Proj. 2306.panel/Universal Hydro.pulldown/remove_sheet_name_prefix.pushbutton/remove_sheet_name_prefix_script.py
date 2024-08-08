#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Remove the sheet name underscore prefix."
__title__ = "Remove Sheet Name Prefix Underscore"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def remove_sheet_name_prefix():
    

    t = DB.Transaction(doc, __title__)
    t.Start()
    for sheet in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements():
        if sheet.Name.startswith("_"):
            sheet.Name = sheet.Name.lstrip("_")
    t.Commit()

"""
def try_catch_error(func):
    def wrapper(*args, **kwargs):
        print("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            return func(*args, **kwargs)
        except Exception as e:
            print(str(e))
            return "Wrapper func for EA Log -- Error: " + str(e)
    return wrapper
"""
"""
    phase_provider = DB.ParameterValueProvider( DB.ElementId(DB.BuiltInParameter.ROOM_PHASE))
    phase_rule = DB.FilterElementIdRule(phase_provider, DB.FilterNumericEquals(), phase.Id)
    phase_filter = DB.ElementParameterFilter(phase_rule)
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WherePasses(phase_filter).WhereElementIsNotElementType().ToElements()
    return all_rooms
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    remove_sheet_name_prefix()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)


