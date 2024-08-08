#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Find the modular marker family that have the EOS instance parameter turned on/off."
__title__ = "73_find_EOS_in_FOG_family"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def find_EOS_in_FOG_family():

    detail_items = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_DetailComponents).WhereElementIsNotElementType().ToElements()

    def is_marker(x):
        if not hasattr(x, "Symbol"):
            return False

        return "Module Marker_" in x.Symbol.FamilyName


    detail_items = filter(is_marker , detail_items)
    level_check_list = ["N3 - LVL 1",
                        "N3 - LVL 2",
                        "N3 - LVL 3",
                        "N3 - LVL 4",
                        "N3 - LVL 5",
                        "N3 - LVL 6",
                        "N3 - LVL 7",
                        "N3 - LVL 8",
                        "N3 - LVL 9"
                        ]
    for marker in  detail_items:
        #print x
        #print x.Symbol.FamilyName
        #owner_view =  doc.GetElement(DB.ElementId(x.OwnerViewId.IntegerValue) )
        owner_view =  doc.GetElement(marker.OwnerViewId )
        level_name = owner_view.GenLevel.Name
        if level_name in level_check_list:
            if not marker.LookupParameter("has EOS line"):
                continue
            has_EOS = True if marker.LookupParameter("has EOS line").AsInteger() else False
            if has_EOS:
                print("{}--has instance EOS = {}--{}".format(owner_view.Name,
                                        has_EOS,
                                        output.linkify(marker.Id, title = "Click me to zoom in")))
    pass
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    find_EOS_in_FOG_family()
