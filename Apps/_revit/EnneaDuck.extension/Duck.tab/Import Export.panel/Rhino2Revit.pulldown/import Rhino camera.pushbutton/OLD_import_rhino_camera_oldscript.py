#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Create Revit perspective views based on Rhino cameras, this is handy for Revit Enscape view recreation."
__title__ = "Import\nRhino camera"
__youtube__ = "https://youtu.be/vBPvwEmu584"
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY

from EnneadTab.REVIT import REVIT_FORMS
from EnneadTab import ERROR_HANDLE
import ENNEAD_LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
from rpw.extras.rhino import Rhino
"""
>>> pt1 = rc.Geometry.Point3d(0,0,0)
>>> pt2 = rc.Geometry.Point3d(10,10,0)
>>> line1 = rc.Geometry.Line(pt1, pt2)
>>> line1.Length
14.142135623730951
>>>
>>> pt1 = rc.Geometry.Point3d(10,0,0)
>>> pt2 = rc.Geometry.Point3d(0,10,0)
>>> line2 = rc.Geometry.Line(pt1, pt2)
>>>
>>> rc.Geometry.Intersect.Intersection.LineLine(line1, line2)
(True, 0.5, 0.5)
>>>
>>> file3dm = f = rc.FileIO.File3dm()
>>> file3md_options = rc.FileIO.File3dmWriteOptions()
>>> file3dm.Objects.AddLine(line1)
>>> filepath = 'c:/folder/test.3dm'
>>> file3dm.Write(filepath, file3md_options)
"""

def get_threeD_view_type():
    view_family_types = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()
    return filter(lambda x: x.ViewFamily == DB.ViewFamily.ThreeDimensional, view_family_types)[0]

def get_XYZ_from_data(data):

    global UNIT_FT
    global UNIT_MM
    global UNIT_M
    global UNIT_INCH
    if UNIT_MM:
        data = [EA_UTILITY.mm_to_internal(x) for x in data]
    elif UNIT_M:
        data = [EA_UTILITY.mm_to_internal(x / 1000.0) for x in data]
    elif UNIT_FT:
        pass
    elif UNIT_INCH:
        data = [x / 12.0 for x in data]
    else:
        print("Someting is wrong.")

    x, y, z = data
    return DB.XYZ(x, y, z)

def import_camera_action(view_info):
    print("----processing camera: " + view_info.Name)
    print(view_info.Viewport.CameraLocation)

    rhino_camera_position = get_XYZ_from_data(view_info.Viewport.CameraLocation)
    rhino_camera_direction = get_XYZ_from_data(view_info.Viewport.CameraDirection)
    rhino_camera_up_direction = get_XYZ_from_data(view_info.Viewport.CameraY)




    print(rhino_camera_direction)

    new_view = DB.View3D.CreatePerspective(doc, get_threeD_view_type().Id)
    global RHINO_NAME
    new_view.Name = view_info.Name + "_imported from Rhino_{}".format(RHINO_NAME)
    #revit_camera = DB.DirectContext3D.Camera()

    new_view.SetOrientation(DB.ViewOrientation3D (rhino_camera_position, rhino_camera_up_direction, rhino_camera_direction))
    return





@ERROR_HANDLE.try_catch_error
def import_rhino_camera():
    #filepath = r"C:\Users\szhang\Desktop\temp1.3dm"
    filepath = EA_UTILITY.get_EA_dump_folder_file("EA_CAMERA_TRANSFER.3dm")
    #filepath = forms.pick_file(file_ext = "3dm")
    #print filepath
    file3dm = Rhino.FileIO.File3dm()
    global RHINO_NAME
    RHINO_NAME = filepath.split("\\")[-1].split(".3dm")[0]
    #print RHINO_NAME
    #print file3dm
    #file3md_options = Rhino.FileIO.File3dmWriteOptions()

    #table_type_filter =
    file3dm = file3dm.Read(filepath)
    if file3dm is None:
        REVIT_FORMS.notification(main_text = "Save as your rhino camera file as Rhino5 for direct import to work.\n\nEnneadtab for Rhino can help with that.",
                                        sub_text = "rpw Rhino module was last published in 2017. That is why direct support is limited.",
                                        window_height = 350,
                                        window_width = 550,
                                        self_destruct = 20)
        return
    #file3dm = file3dm.Read(filepath, Rhino.File3dm.TableTypeFilter.1, Rhino.File3dm.ObjectTypeFilter.2)

    #for view_info in file3dm.Views:
        #print view_info.Name
    global UNIT_FT
    global UNIT_MM
    global UNIT_M
    global UNIT_INCH
    UNIT_M = False
    UNIT_MM = False
    UNIT_FT = False
    UNIT_INCH = False
    unit_options = ["Meter", "Millimeter", "Feet", "Inch"]
    unit = forms.SelectFromList.show(unit_options,
                                    multiselect = False,
                                    button_name = "Confirm Rhino file unit",
                                    title = "What is the unit in that camera file?")
    if unit == unit_options[0]:
        UNIT_M = True
    if unit == unit_options[1]:
        UNIT_MM = True
    if unit == unit_options[2]:
        UNIT_FT = True
    if unit == unit_options[3]:
        UNIT_INCH = True


    named_views = list(file3dm.NamedViews)
    named_views.sort(key = lambda x: x.Name)
    sel_views = forms.SelectFromList.show(named_views,
                                            multiselect = True,
                                            name_attr = "Name",
                                            title = __title__,
                                            button_name = "Import Selected Camera to Revit")
    if not sel_views:
        return
    t = DB.Transaction(doc, "import Rhino camera")
    t.Start()
    map(import_camera_action, sel_views)
    t.Commit()

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    import_rhino_camera()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
