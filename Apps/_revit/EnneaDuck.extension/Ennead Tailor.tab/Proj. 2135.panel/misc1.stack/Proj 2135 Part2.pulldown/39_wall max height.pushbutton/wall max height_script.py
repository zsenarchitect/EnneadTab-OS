#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Find the geometrical max height of walls and store that data at 'Element_Max_Height_Report' parameter"
__title__ = "39_wall max_height"


from pyrevit import script #

import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 

doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def check_max_height(wall):
    predefined_max = wall.LookupParameter("Element_Max_Height_Target").AsDouble()
    if predefined_max == 0:
        return



    highest_pt_Z = -10000

    try:
        grids = wall.CurtainGrid
        panels = [doc.GetElement(x) for x in grids.GetPanelIds()]
        for panel in panels:
            panel_geo = panel.get_Geometry(opt)
            panel_bbox = panel_geo.GetBoundingBox()
            panel_highest_pt_Z = panel_bbox.Max.Z
            highest_pt_Z = max( panel_highest_pt_Z , highest_pt_Z)
    except:
        geo = wall.get_Geometry(opt)
        bbox = geo.GetBoundingBox()
        highest_pt_Z = bbox.Max.Z

    # print highest_pt_Z - predefined_max

    wall.LookupParameter("Element_Max_Height_Report").Set(highest_pt_Z)
    if highest_pt_Z - predefined_max > 0.00001:
        wall.LookupParameter("Element_Max_Height_Result").Set("Bad")
    else:
        wall.LookupParameter("Element_Max_Height_Result").Set("Ok")
    # print EA_UTILITY.internal_to_mm(predefined_max)
################## main code below #####################
output = script.get_output()
output.close_others()

walls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

opt = DB.Options()
opt.IncludeNonVisibleObjects = True
opt.ComputeReferences = True
t = DB.Transaction(doc, "check wall max height")
t.Start()
map(check_max_height, walls)
t.Commit()
# print EA_UTILITY.dialogue()
#ideas:
