#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyrevit import forms
from pyrevit import script
import EA_UTILITY

from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE

from Autodesk.Revit import DB # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__title__ = "Import Rhino Camera"
__doc__ = "Work with Camera exported in Rhino side to recreate the same perspective camera.\n\nIt can be useful for Enscape view recreation in Revit."
__tip__ = True
from rpw.extras.rhino import Rhino


class CameraImporter:
    def __init__(self):
        self.UNIT_FT = self.UNIT_MM = self.UNIT_M = self.UNIT_INCH = False
        self.RHINO_NAME = None

    @staticmethod
    def get_threeD_view_type():
        view_family_types = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()
        return next(filter(lambda x: x.ViewFamily == DB.ViewFamily.ThreeDimensional, view_family_types), None)

    def get_XYZ_from_data(self, data):
        if self.UNIT_MM:
            data = [EA_UTILITY.mm_to_internal(x) for x in data]
        elif self.UNIT_M:
            data = [EA_UTILITY.mm_to_internal(x / 1000.0) for x in data]
        elif self.UNIT_FT:
            pass
        elif self.UNIT_INCH:
            data = [x / 12.0 for x in data]
        else:
            print("Something is wrong.")
        x, y, z = data
        return DB.XYZ(x, y, z)

    def import_camera_action(self, view_info):
        print("----processing camera: " + view_info.Name)
        print(view_info.Viewport.CameraLocation)

        rhino_camera_position = self.get_XYZ_from_data(view_info.Viewport.CameraLocation)
        rhino_camera_direction = self.get_XYZ_from_data(view_info.Viewport.CameraDirection)
        rhino_camera_up_direction = self.get_XYZ_from_data(view_info.Viewport.CameraY)

        new_view = DB.View3D.CreatePerspective(doc, self.get_threeD_view_type().Id)
        new_view.Name = view_info.Name + "_imported from Rhino_{}".format(self.RHINO_NAME)
        new_view.SetOrientation(DB.ViewOrientation3D(rhino_camera_position, rhino_camera_up_direction, rhino_camera_direction))

    def import_rhino_camera(self):
        filepath = EA_UTILITY.get_EA_dump_folder_file("EA_CAMERA_TRANSFER.3dm")
        self.RHINO_NAME = filepath.split("\\")[-1].split(".3dm")[0]

        file3dm = Rhino.FileIO.File3dm()
        file3dm = file3dm.Read(filepath)

        if file3dm is None:
            REVIT_FORMS.notification(main_text="Save as your rhino camera file as Rhino5 for direct import to work.",
                                             sub_text="rpw Rhino module was last published in 2017. That's why direct support is limited.",
                                             window_height=350,
                                             window_width=550,
                                             self_destruct=20)
            return

        unit_options = ["Meter", "Millimeter", "Feet", "Inch"]
        unit = forms.SelectFromList.show(unit_options, multiselect=False, button_name="Confirm Rhino file unit", title="What is the unit in that camera file?")
        self.set_unit(unit)

        named_views = list(file3dm.NamedViews)
        named_views.sort(key=lambda x: x.Name)
        sel_views = forms.SelectFromList.show(named_views, multiselect=True, name_attr="Name", title="Import Rhino Camera", button_name="Import Selected Camera to Revit")
        if not sel_views:
            return

        t = DB.Transaction(doc, "import Rhino camera")
        t.Start()
        for view in sel_views:
            self.import_camera_action(view)
        t.Commit()

    def set_unit(self, unit):
        self.UNIT_M = unit == "Meter"
        self.UNIT_MM = unit == "Millimeter"
        self.UNIT_FT = unit == "Feet"
        self.UNIT_INCH = unit == "Inch"
        
        
        
@ERROR_HANDLE.try_catch_error()
def main():
    importer = CameraImporter()
    importer.import_rhino_camera()



########################################################
if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    main()