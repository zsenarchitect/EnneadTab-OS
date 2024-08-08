#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "update_level_relative_value"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_GEOMETRY
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error
def update_level_relative_value(doc):
    all_levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()

    all_levels = REVIT_SELECTION.filter_elements_changable(all_levels)

    # project_position_info = REVIT_GEOMETRY.get_project_location_info(doc)
    # project_base_pt = project_position_info.GetProjectPosition (DB.BasePoint.GetProjectBasePoint(doc).Position)

    project_base_pt_obj = DB.BasePoint.GetProjectBasePoint(doc)
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    for level in all_levels:
        relative_elevation = level.Elevation - project_base_pt_obj.LookupParameter("Elev").AsDouble() #project_base_pt.Elevation
        level.LookupParameter("Level_$Alternate Datum_Elevation").Set(relative_elevation)
    t.Commit()


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    update_level_relative_value(doc)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







