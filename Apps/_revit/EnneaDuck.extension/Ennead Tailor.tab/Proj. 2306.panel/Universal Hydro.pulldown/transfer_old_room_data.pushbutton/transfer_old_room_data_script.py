#!/usr/bin/python
# -*- coding: utf-8 -*-


__doc__ = "Transfer room occupancy load data from old parameter to new parameter. See detail in script"
__title__ = "Transfer Old Room Data"

# from pyrevit import forms #
from pyrevit import script
# from pyrevit import revit #
# import EA_UTILITY

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore  
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def transfer_old_room_data():
    pass
    t = DB.Transaction(doc, __title__)
    t.Start()
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(
        DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

    for room in all_rooms:

        # make sure this parameter has at least 0.
        # old_para = room.LookupParameter("Rooms_$LS_Occupancy Manual")
        new_para = room.LookupParameter("Rooms_Occupancy Manual")
        if new_para.AsInteger() == 0:
           
            new_para.Set(-1)

    t.Commit()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    transfer_old_room_data()
    ENNEAD_LOG.use_enneadtab(
        coin_change=20, tool_used=__title__.replace("\n", " "), show_toast=True)

