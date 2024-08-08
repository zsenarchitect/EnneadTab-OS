#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Get rooms that is overlapping other rooms, and tag them in views from selected sheets."
__title__ = "80_tag_room_too_high"

from pyrevit import forms
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def get_element_warning(element, key_word_in_description = None):
    all_warnings = doc.GetWarnings()
    for failure_msg in all_warnings:
        if key_word_in_description is not None and key_word_in_description not in failure_msg.GetDescriptionText ():
            continue
        els = failure_msg.GetFailingElements ()
        if element.Id in list(els):
            return failure_msg.GetDescriptionText ()
    return None


def process_view(view):
    print("--working on view: " + view.Name)
    rooms = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
    for room in rooms:
        warning = get_element_warning(room, "Room volumes overlap")
        if not warning:
            continue
        #type = get_room_tag_type_by_name("TAG_Room_internal check")
        #type = get_room_tag_type_by_name("main_check")
        add_tag_to_room(view, "main_check", room)
    pass

def add_tag_to_room(view, type_name, room):
    X, Y = room.Location.Point.X, room.Location.Point.Y
    UV = DB.UV(X, Y)
    tag = doc.Create.NewRoomTag(DB.LinkElementId(room.Id), UV, view.Id)
    print("----found room overlay, checker tag added.")
    type_ids = tag.GetValidTypes()
    for type_id in type_ids:
        type = doc.GetElement(type_id)
        #print type.LookupParameter("Type Name").AsString()
        if type.LookupParameter("Type Name").AsString() == type_name:
            tag.ChangeTypeId(type.Id)
            break
            #tag.RoomTagType = type
    else:
        print("Change find this checker tag type. Tool terminated.")
        script.exit()

def OLD_get_room_tag_type_by_name(name, tag):
    room_tags_types = tag.GetValidTypes()
    for type in room_tags_types:
        if type.LookupParameter("Type Name").AsString() == name:
            return type
    return None

def tag_room_too_high():
    sheets = forms.select_sheets(title = "what sheets to mark?")

    if not sheets:
        return
    if not type:
        return

    for i, sheet in enumerate(sheets):
        print("{} of {}. working on sheet: {}".format(i + 1, len(sheets), sheet.Name))
        for view_id in sheet.GetAllPlacedViews():
            view = doc.GetElement(view_id)
            process_view(view)

    pass
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    t = DB.Transaction(doc, "tag bad room")
    t.Start()
    tag_room_too_high()
    t.Commit()
