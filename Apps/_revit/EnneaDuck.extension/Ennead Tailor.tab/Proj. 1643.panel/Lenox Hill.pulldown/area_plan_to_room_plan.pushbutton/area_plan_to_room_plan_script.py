#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Convert all area boundary line to room seperation line, area to room in current view"
__title__ = "AreaPlan to RoomPlan"

from pyrevit import forms #
from pyrevit import script #
import System

from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()



STORAGE_TYPE_MAP = {
    DB.StorageType.String: str,
    DB.StorageType.Integer: System.Int32,
    DB.StorageType.Double: System.Double,
    DB.StorageType.ElementId: DB.ElementId,
}


@ERROR_HANDLE.try_catch_error()
def area_plan_to_room_plan():
    views = forms.select_views()
    if not views:
        return


    t = DB.Transaction(doc, __title__)
    t.Start()
    map(process_view, views)    
    t.Commit()


def process_view(view):

    all_area_boundary_lines = DB.FilteredElementCollector(doc, view).OfCategory(DB.BuiltInCategory.OST_AreaSchemeLines).ToElements()

    level_id = view.GenLevel.Id
    sketch_plane = DB.SketchPlane.Create(doc, level_id)

    # for area_line in list(all_area_boundary_lines)[:10]:
        # print(area_line.Subcategory)
    crv_arr = DB.CurveArray()
    for area_line in all_area_boundary_lines:
        crv_arr.Append(area_line.GeometryCurve)

    sp_lines_arr = doc.Create.NewRoomBoundaryLines (sketch_plane, crv_arr, doc.ActiveView)

    print (output.linkify(view.Id, title = view.Name))

    all_areas = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()

    for area in all_areas:
        print(area.Location.Point)
        new_room = doc.Create.NewRoom(view.GenLevel, DB.UV(area.Location.Point.X, area.Location.Point.Y))

        for para in area.Parameters:
            
            if new_room.LookupParameter(para.Definition.Name) is not None:

                if new_room.LookupParameter(para.Definition.Name).IsReadOnly:
                    continue
                if para.StorageType == DB.StorageType.String:
                    old_value = para.AsString()
                elif para.StorageType == DB.StorageType.Integer:
                    old_value = para.AsInteger()
                elif para.StorageType == DB.StorageType.Double:
                    old_value = para.AsDouble()
                elif para.StorageType == DB.StorageType.ElementId:
                    old_value = para.AsElementId()

                target_type = STORAGE_TYPE_MAP.get(para.StorageType)
                try:
                    # new_room.LookupParameter(para.Definition.Name).Set(old_value)
                    new_room.LookupParameter(para.Definition.Name).Set.Overloads[target_type](old_value)
                    print ("{} transfered!.".format(para.Definition.Name))
                except Exception as e:
                    print ("{} failed to transfer! Becasue {}.".format(para.Definition.Name, e))


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    area_plan_to_room_plan()
    







