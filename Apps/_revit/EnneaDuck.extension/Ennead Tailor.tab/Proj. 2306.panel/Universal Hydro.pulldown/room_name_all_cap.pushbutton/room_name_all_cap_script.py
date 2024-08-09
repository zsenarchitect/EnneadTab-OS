#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Make all room name as full CAP"
__title__ = "CAP_ALL_ROOM_NAME"

# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def room_name_all_cap():
    pass

    t = DB.Transaction(doc, __title__)
    t.Start()
    for room in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements():
        # make room name upper case
        new_name = room.LookupParameter("Name").AsString().upper()
        room.LookupParameter("Name").Set(new_name)


    t.Commit()
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    room_name_all_cap()
    





