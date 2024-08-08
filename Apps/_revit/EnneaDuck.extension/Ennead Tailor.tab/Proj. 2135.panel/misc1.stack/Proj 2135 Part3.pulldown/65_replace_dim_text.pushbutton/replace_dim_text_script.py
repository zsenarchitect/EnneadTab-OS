#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Replace the dim text that is below the dim number in current document from A to B. \n\nFor example, changing from 'FOG' to 'F.O.G.'"
__title__ = "65_replace_dim_text"

from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def replace_dim_text():

    dims = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Dimensions).WhereElementIsNotElementType().ToElements()
    text_to_search = forms.ask_for_string(default = "A.B.C.", prompt = "dim text you dont like")
    text_to_replace = forms.ask_for_string(default = "ABC", prompt = "dim text to replace that with")
    map(lambda x: fix_dim(x, text_to_search, text_to_replace), dims)


def fix_dim(dim, text_to_search, text_to_replace):
    if dim.NumberOfSegments == 0:
        if dim.Below == text_to_search:
            dim.Below = text_to_replace
            print(dim.Id)
        return

    for dim_seg in dim.Segments:
        if dim_seg.Below == text_to_search:
            dim_seg.Below = text_to_replace
            print(dim.Id)

    pass
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    t = DB.Transaction(doc, "replace dim text")
    t.Start()
    replace_dim_text()
    t.Commit()
    print("Tool finished")
