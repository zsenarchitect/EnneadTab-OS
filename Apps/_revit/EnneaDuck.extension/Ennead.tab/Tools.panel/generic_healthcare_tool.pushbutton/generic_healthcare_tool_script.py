#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "HealthCare\nHelper"
__tip__ = True
# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import USER, ERROR_HANDLE, LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
            



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def generic_healthcare_tool(doc, show_log):
    if not USER.IS_DEVELOPER:
        return
    
    note = """TO-DO:
here is what will the tool auto run:

1, get all the area, get their names, make sure all area is defined within a predefined list of HealthCare Category
(the name list should come from a excel that define the names and color, DO NOT PUT RGB value in the eexcel, expect future update)


"""
    print (note)

    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
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
    generic_healthcare_tool(doc, show_log=True)
    


