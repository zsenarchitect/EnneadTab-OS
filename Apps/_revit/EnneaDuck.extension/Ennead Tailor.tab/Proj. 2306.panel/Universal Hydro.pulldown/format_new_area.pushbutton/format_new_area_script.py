#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Make sure all areas have at least a valid discount data.\n\nMake sure all areas have department data."
__title__ = "(Depreciated)Format New Area"

# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def format_new_area():
  
    t = DB.Transaction(doc, __title__)
    t.Start()
    all_areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    all_areas = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_areas)
    
    
    bad_areas = set()
    for area in all_areas:
        # fix area that does not have discount factor data
        para = area.LookupParameter("Discount Factor")
        if not para.HasValue:
            para.Set(1.0)
            bad_areas.add(area)


        # highlight area that has not department data
        para = area.LookupParameter("Area Department")
        if not para.HasValue:
            para.Set("Department Undefined")
            bad_areas.add(area)
    t.Commit()

    if len(bad_areas) >0:
        print ("\n\nThe following areas are corrected:")
        for area in bad_areas:
            print (output.linkify(area.Id, title = area.LookupParameter("Name").AsString()))
    else:
        print ("All look good.")
        
    EnneadTab.NOTIFICATION.messenger("Format New Area All look good.")
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
    format_new_area()
    


