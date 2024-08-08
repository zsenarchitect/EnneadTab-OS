#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Check if all of your grids and elevations is orthoganal."
__title__ = "35_Elevation and Grid orth-direction"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


################## main code below #####################
output = script.get_output()
output.close_others()

grids = DB.FilteredElementCollector(doc).OfClass(DB.Grid).WhereElementIsNotElementType().ToElements()

for grid in grids:
    print("----")
    print(grid.Name)
    angle_to_X = grid.Curve.Direction.AngleTo(DB.XYZ(1,0,0))
    angle_to_Y = grid.Curve.Direction.AngleTo(DB.XYZ(0,1,0))
    print(EA_UTILITY.radian_to_degree(angle_to_X), EA_UTILITY.radian_to_degree(angle_to_Y))
print("*"*20)

views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
elevations = filter(lambda x: x.ViewType == DB.ViewType.Elevation, views)
for view in elevations:
    print("-------")
    print(view.Name)
    print(view.ViewDirection)
    x, y, z = view.ViewDirection.X, view.ViewDirection.Y, view.ViewDirection.Z
    print(x, y, z)
    """
    for item in [x, y, z]:
        if item not in [0.0, 1.0, -1.0]:
            print("*************************not orthoganal, {}".format(output.linkify(view.Id, title = "go to view")))
    """
    if x not in [0.0, 1.0, -1.0]:
        print("*************************not orthoganal, {}".format(output.linkify(view.Id, title = "go to view")))

    angle_to_X = view.ViewDirection.AngleTo(DB.XYZ(1,0,0))
    angle = EA_UTILITY.radian_to_degree(angle_to_X)
    print("angle to X axis = {}".format(angle))
