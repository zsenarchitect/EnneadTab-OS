#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Find the dims of internal dim type, and update the selection filter set for filter control."
__title__ = "44.1_update internal dim selection set"


from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def redefine_selection_set(set_name):
    all_filters = DB.FilteredElementCollector(doc).OfClass(DB.FilterElement).ToElements()
    for filter in all_filters:
        if filter.Name == set_name:
            #filter.Clear()
            break
    else:
        filter = DB.SelectionFilterElement.Create(doc, set_name)
    return filter

def add_markup_dims_to_set(selection_set):
    all_dims = DB.FilteredElementCollector(doc).OfClass(DB.Dimension).WhereElementIsNotElementType().ToElements()
    markup_dims = filter(lambda x: x.DimensionType.LookupParameter("Type Name").AsString().lower() in ["markup", "sketch"], all_dims)
    selection_set.SetElementIds(EA_UTILITY.list_to_system_list([x.Id for x in markup_dims]))
################## main code below #####################
output = script.get_output()
output.close_others()


# modify each template
t = DB.Transaction(doc, "update internal dim selection set")
t.Start()

selection_set = redefine_selection_set("dim_internal")
add_markup_dims_to_set(selection_set)

t.Commit()
print("tool finish")
