#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Make sure all sheets have a default Print_In_Color value.\n\nMake sure all sheets show in shecule"
__title__ = "(Depreciated)Format New Sheets"

# from pyrevit import forms #
from pyrevit import script #

import EA_UTILITY

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def format_new_sheet():
    pass


    t = DB.Transaction(doc, __title__)
    t.Start()
    key_para = "Print_In_Color"
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    all_sheets = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_sheets)
    
    all_sheets = list(all_sheets)
    all_sheets.sort(key = lambda x: x.SheetNumber)

    bad_sheets = set()
    for sheet in all_sheets:
        para = sheet.LookupParameter(key_para)
        if not para.HasValue:
            print("Assign default Print In Color value at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
            
            para.Set(0)
            bad_sheets.add(sheet)

        if not sheet.LookupParameter("Appears In Sheet List").AsInteger():
            sheet.LookupParameter("Appears In Sheet List").Set(1)
            bad_sheets.add(sheet)
           
  
    t.Commit()

    if len(bad_sheets) >0:
        print ("\n\nThe following sheets are corrected:")
        for sheet in bad_sheets:
            print (output.linkify(sheet.Id, title = sheet.SheetNumber + " - " + sheet.Name))
    else:
        print ("All look good.")
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
    format_new_sheet()
    


