#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Get door size data from old file. Apply to current file by matching GUID."
__title__ = "74_bring_size_from_old_door"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore



def get_file_path():
    folder = EA_UTILITY.get_EA_setting_folder()
    file = "door_size_record.txt"
    return "{}\{}".format(folder, file)



def update_current_door_size():
    doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

    data = EA_UTILITY.read_txt_as_list(filepath = get_file_path())

    door_size_dict = dict()
    for x in data:
        #print x
        id, width = x.split("$$")
        door_size_dict[id] = float(width)

    t = DB.Transaction(doc, "update door size")
    t.Start()
    for door in doors:
        para = door.LookupParameter("Door Leaf Width")
        if para is None:
            continue
        #print door.GroupId
        if door.GroupId.IntegerValue  != -1:
            print("Door inside a group---->{}".format(output.linkify(door.Id)))
            continue

        try:
            id = door.UniqueId
            para.Set(door_size_dict[id])
        except Exception as e:
            pass
            #print door.Id
            print (e)
    t.Commit()

def record_old_door_size():
    doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

    OUT = []
    for door in doors:
        para = door.LookupParameter("#door leaf")
        if para is None:
            continue
        unique_ID = door.UniqueId
        door_leaf = para.AsDouble()
        OUT.append("{}$${}".format(unique_ID, door_leaf))

    filepath = get_file_path()
    EA_UTILITY.save_list_to_txt(OUT, filepath)



def bring_size_from_old_door():
    opt = ["record old door size", "update current door size"]
    res = EA_UTILITY.dialogue(options = opt)
    if res == opt[0]:
        record_old_door_size()
    else:
        update_current_door_size()
    pass
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    bring_size_from_old_door()
