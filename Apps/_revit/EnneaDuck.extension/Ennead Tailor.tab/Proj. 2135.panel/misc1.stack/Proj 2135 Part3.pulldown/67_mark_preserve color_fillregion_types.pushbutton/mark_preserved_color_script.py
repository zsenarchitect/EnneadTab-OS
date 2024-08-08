#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sometimes you want to set certain filled region and detail item to be graphically controlled seperately from the category graphic. So you can use filter to assign special graphic. But the setting inside the type parameter might not be reflected on the type name. So this tool will lookup for those conditions and append '_preserved color' in type name os it is easier to be found."
__title__ = "67_mark preserve color fillregion and detail item type"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def OLD_get_para_by_name(type, name):
    for para in type.Parameters:
        para_name = para.Definition.Name
        #print "---" + para_name
        if name in para_name:
            return para
    return None

def OLD_process_fillregion_type(type):
    key = "Preserved Color"
    """
    print("***")
    #print type
    print(type.LookupParameter("Type Name").AsString())
    #print type.FamilyName
    print(get_para_by_name(type, "Type Comments").AsString())
    if get_para_by_name(type, "Type Comments").AsString() is not None:
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    return
    print(type.LookupParameter("Line Weight").AsString())
    return
    for para in type.Parameters:
        print(para.Definition.Name)
    """
    type_comments = type.LookupParameter("Type Comments").AsString()
    if type_comments is None:
        type_comments = ""
    if key in type_comments:
        current_name = type.LookupParameter("Type Name").AsString()
        if key in current_name:
            return
        new_name = current_name + "_" + key
        #type.LookupParameter("Type Name").Set(new_name)
        type.Name = new_name
    else:
        current_name = type.LookupParameter("Type Name").AsString()
        if key in current_name:
            new_name = current_name.replace("_" + key, "")
            #type.LookupParameter("Type Name").Set(new_name)
            type.Name = new_name


def process_detailitem_type(type):
    if "Repeating Detail" in type.FamilyName:
        return

    #print type.LookupParameter("Type Name").AsString()
    key = "Preserved Color"
    type_comments = type.LookupParameter("Type Comments").AsString()
    if type_comments is None:
        type_comments = ""
    if key in type_comments:
        current_name = type.LookupParameter("Type Name").AsString()
        if key in current_name:
            return
        new_name = current_name + "_" + key
        #type.LookupParameter("Type Name").Set(new_name)
        type.Name = new_name
        print("name change: {}--->{}".format(current_name, new_name))
    else:
        current_name = type.LookupParameter("Type Name").AsString()
        if key in current_name:
            new_name = current_name.replace("_" + key, "")
            #type.LookupParameter("Type Name").Set(new_name)
            type.Name = new_name
            print("name change: {}--->{}".format(current_name, new_name))

def run():
    #fill_region_types = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).ToElements()
    detail_item_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_DetailComponents).WhereElementIsElementType().ToElements()
    """
    this includes filled region and repeating item and common detail component
    """


    #map(process_fillregion_type, fill_region_types)
    map(process_detailitem_type, detail_item_types)

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    t = DB.Transaction(doc, "mark_preserve_color")
    t.Start()
    run()
    t.Commit()
