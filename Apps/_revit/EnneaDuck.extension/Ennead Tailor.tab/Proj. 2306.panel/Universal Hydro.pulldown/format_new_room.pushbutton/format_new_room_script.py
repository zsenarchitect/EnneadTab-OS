#!/usr/bin/python
# -*- coding: utf-8 -*-


__doc__ = "Make sure all room 'Rooms_$LS_Occupancy Manual' is at-least zero.\n\nAlso transfer the name of the life safety key to the title so you can see it on tags."
__title__ = "(Depreciated)Format New Rooms"

# from pyrevit import forms #
from pyrevit import script
# from pyrevit import revit #
# import EA_UTILITY
import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore  
# from Autodesk.Revit import UI # pyright: ignore
try:
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
except:
    pass


def format_new_room(doc, show_log = True):
    pass

    t = DB.Transaction(doc, __title__)
    t.Start()
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(
        DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

    all_rooms = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_rooms)
    bad_rooms = set()
    changed_rooms = set()
    for room in all_rooms:

        # make sure this parameter has at least 0.
        para = room.LookupParameter("Rooms_Occupancy Manual")
        if not para.HasValue:
            para.Set(-1)
            bad_rooms.add(room)

        # update the title
        room_style_id = room.LookupParameter("Life Safety").AsElementId()
        if room_style_id.IntegerValue == -1:
            if show_log:
                print("This room has no life safety style defined--->{}".format(
                output.linkify(room.Id, title=room.LookupParameter("Name").AsString())))
            style_name = "--No Life Safety Style Defined--"
            bad_rooms.add(room)

        else:
            room_style = doc.GetElement(room_style_id)
            style_name = room_style.Name

        if room.LookupParameter("Rooms_Occupancy Style Title").AsString() != style_name:
            room.LookupParameter("Rooms_Occupancy Style Title").Set(style_name)
            changed_rooms.add(room)

    t.Commit()

    if len(changed_rooms) > 0:
        print("\nThe {} rooms life safety title are updated.".format(len(changed_rooms)))
        # for room in changed_rooms:
        #     print(output.linkify(
        #         room.Id, title=room.LookupParameter("Name").AsString()))
            
    if len(bad_rooms) > 0:
        print("\n\nThe {} rooms need attention, they have no life safety style assigned.".format(len(bad_rooms)))
        # for room in bad_rooms:
        #     print(output.linkify(
        #         room.Id, title=room.LookupParameter("Name").AsString()))
    else:
        if show_log:
            print("All look good.")


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
    format_new_room(doc)
    ENNEAD_LOG.use_enneadtab(
        coin_change=20, tool_used=__title__.replace("\n", " "), show_toast=True)

