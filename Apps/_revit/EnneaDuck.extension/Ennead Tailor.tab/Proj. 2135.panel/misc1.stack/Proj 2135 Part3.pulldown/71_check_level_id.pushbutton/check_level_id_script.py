#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Print out all levels, ranked by elevation, to show level names and its level id data"
__title__ = "71_check_level_id"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def check_level_id():
    levels = list(DB.FilteredElementCollector(doc).OfClass(DB.Level).WhereElementIsNotElementType().ToElements())

    levels.sort(key = lambda x: x.Elevation, reverse = True)
    for level in levels:
        print("{}:{}:{}".format(EA_UTILITY.internal_to_mm(level.Elevation), level.Name, level.Id))

    print("\n\n\n")
    levels.sort(key = lambda x: x.Id, reverse = True)
    for level in levels:
        print("{}:{}:{}".format(EA_UTILITY.internal_to_mm(level.Elevation), level.Name, level.Id))

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    check_level_id()
