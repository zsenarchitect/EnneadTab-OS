#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "For views on selected sheets, inspect if there are local graphic override or local hidden objects that is not controlled by template."
__title__ = "Inspect Local\nGraphic Override"

from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS
from EnneadTab import ERROR_HANDLE, LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def inspect_local_graphic_override():

    sheets = forms.select_sheets(title = "sheets with views to check")
    if sheets is None:
        return

    opts = ["Review in Revit", ["Later export to excel", "You can save the output window and open in Excel, use ',' as common delimiter"]]
    res = REVIT_FORMS.dialogue(options = opts,
                                                main_text = "How do you want to review it?")
    is_excel_mode = True if res == opts[1][0] else False
    unique_cate = set()
    t = DB.Transaction(doc, "detect hidden elements")
    t.Start()
    counter = 1
    for i, sheet in enumerate(sheets):
        if not is_excel_mode:
            print("\n\n----{}/{}: {}-{}-----".format(i + 1, len(sheets), sheet.SheetNumber, sheet.Name))
        for view_id in sheet.GetAllPlacedViews():
            view = doc.GetElement(view_id)
            view.EnableRevealHiddenMode ()
            elements = DB.FilteredElementCollector(doc, view_id).WhereElementIsNotElementType().ToElements()
            for element in elements:
                if not hasattr(element.Category, "Name"):
                    continue
                if element.Category.Name in ["Views"]:
                    continue

                if view.GetCategoryHidden (element.Category.Id):
                    continue

                unique_cate.add( element.Category.Name)
                #print element
                if element.IsHidden(view):
                    if is_excel_mode:
                        print("{},{},Hidden,{}".format(counter,
                                                 "[{}]: {}".format(element.Category.Name, element.Id),
                                                view.Name))
                    else:
                        print("[{}]---{} is currently hidden in view: <{}>.".format(counter,
                                                                                    output.linkify(element.Id, title = "[{}]: {}".format(element.Category.Name, element.Id)),
                                                                                    output.linkify(view.Id, title = view.Name)))
                    counter += 1

                cate_graphic = view.GetCategoryOverrides(element.Category.Id)
                element_graphic = view.GetElementOverrides (element.Id)
                check_list = ["CutBackgroundPatternColor",
                                "CutBackgroundPatternId",
                                "CutForegroundPatternColor",
                                "CutForegroundPatternId",
                                "CutLineColor",
                                "CutLinePatternId",
                                "CutLineWeight",
                                "Halftone",
                                "IsCutBackgroundPatternVisible",
                                "IsCutForegroundPatternVisible",
                                "IsSurfaceBackgroundPatternVisible",
                                "IsSurfaceForegroundPatternVisible",
                                "ProjectionLineColor",
                                "ProjectionLinePatternId",
                                "ProjectionLineWeight",
                                "SurfaceBackgroundPatternColor",
                                "SurfaceBackgroundPatternId",
                                "SurfaceForegroundPatternColor",
                                "SurfaceForegroundPatternId",
                                "Transparency"]
                for graphic_item in check_list:
                    cate_property, element_property = getattr(cate_graphic, graphic_item), getattr(element_graphic, graphic_item)
                    property_type = str(cate_property.GetType()).lower()
                    is_graphic_same = True

                    if "color" in property_type:
                        #if cate_property.IsValid
                        if not element_property.IsValid:
                            continue
                        #print cate_property.IsValid
                        #print output.linkify(element.Id)
                        if not cate_property.IsValid or\
                            cate_property.Blue != element_property.Blue or\
                            cate_property.Green != element_property.Green or\
                            cate_property.Red != element_property.Red:
                            is_graphic_same = False

                    if "elemendid" in property_type:
                        if cate_property.Id != element_property.Id:
                            is_graphic_same = False

                    if "int" in property_type:
                        if cate_property != element_property:
                            is_graphic_same = False

                    if "bool" in property_type:
                        if cate_property != element_property:
                            is_graphic_same = False



                    if is_graphic_same == False:
                        if is_excel_mode:
                            print("{},{},{},{}".format(counter,
                                                    "[{}]: {}".format(element.Category.Name, element.Id),
                                                    graphic_item,
                                                    view.Name))
                        else:
                            print ("[{}]---{} is has local {} override in view: <{}>.".format(counter,
                                                                                            output.linkify(element.Id, title = "[{}]: {}".format(element.Category.Name, element.Id)),
                                                                                            graphic_item,
                                                                                            output.linkify(view.Id, title = view.Name)))
                        
                        counter += 1


    t.Commit()
    if not is_excel_mode:
        print ("\n\nDebug Note: ")
        print ("Unique Category")
        print (unique_cate)
    return





    pass
################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    inspect_local_graphic_override()
