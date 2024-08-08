#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Get the sheet order parameter value to a new format."
__title__ = "Transfer Sheet Order"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def transfer_sheet_order():
    sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()



    t = DB.Transaction(doc, __title__)
    t.Start()
    500
    for sheet in sheets:
        if sheet.LookupParameter("Discipline").AsString() == "ARCHITECTURAL":
            data = sheet.LookupParameter("Sheet_$Order").AsInteger()
            sheet.LookupParameter("Sheet_$Order").Set(500 + data*10)
        """
        data = sheet.LookupParameter("Sheet Order").AsString()
        if not data:
            continue
        print(data)
        try:
            sheet.LookupParameter("Sheet_$Order").Set(int(data))
            sheet.LookupParameter("Sheet Order").Set("Old_{}".format(data))
        except:
            pass
        """

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
    transfer_sheet_order()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)


