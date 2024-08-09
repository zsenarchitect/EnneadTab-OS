#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "For composite floor element, recreate the finish and structrue slab as seperate element. It will use the source footprint for both outcomes."
__title__ = "57_break composite floor"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument

def get_floor_type_by_name(name):
    all_types = DB.FilteredElementCollector(doc).OfClass(DB.FloorType).ToElements()

    """
    print("####looking for " + name)
    for x in all_types:
        pass
        print(x.LookupParameter("Type Name").AsString())
    print("####")
    """
    return filter(lambda x:x.LookupParameter("Type Name").AsString() == name, all_types)[0]

def get_info_from_floortype(type_name, checked_type_dict):
    for key, value in checked_type_dict.items():
        if key == type_name:
            finish_thickness, structural_thickness = value
            return finish_thickness, structural_thickness

def process_floor(floor):

    checked_type_dict = {"Composite_150mm+120mm": (150,120),
                        "Composite_50mm+120mm":(50,120),
                        "Composite_150mm+120mm_BULKHEAD":(150,120),
                        "Composite_Roof_600mm+120mm(OCCUPIABLE)":(600,120)}
    if floor.Name not in checked_type_dict.keys():
        print("this type not sure what to do: " + floor.Name)
        return

    finish_thickness, structural_thickness = get_info_from_floortype(floor.Name, checked_type_dict)
    #print finish_thickness, structural_thickness

    copied_floor = DB.ElementTransformUtils.CopyElement(doc, floor.Id, DB.XYZ(0,0,-EA_UTILITY.mm_to_internal(finish_thickness)))[0]
    copied_floor = doc.GetElement(copied_floor)

    finish_type_name = "Finish Floor_{}mm".format(finish_thickness)
    if "BULKHEAD" in floor.Name:
        finish_type_name += "_BULKHEAD"
    if "OCCUPIABLE" in floor.Name:
        finish_type_name += "_OCCUPIABLE"
    if "Roof" in floor.Name:
        finish_type_name = finish_type_name.replace("Finish Floor", "Roof")
    floor.FloorType = get_floor_type_by_name(finish_type_name)
    copied_floor.FloorType = get_floor_type_by_name("Structural Slab_{}mm".format(structural_thickness))
    #current_offset = copied_floor.LookupParameter("Height Offset From Level").AsDouble()
    #copied_floor.LookupParameter("Height Offset From Level").Set(current_offset - EA_UTILITY.mm_to_internal(structural_thickness))



def main():
    selection_ids = uidoc.Selection.GetElementIds ()
    selection = [doc.GetElement(x) for x in selection_ids]
    map(process_floor, selection)




################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    t = DB.Transaction(doc, "break composite floor")
    t.Start()
    main()
    t.Commit()
