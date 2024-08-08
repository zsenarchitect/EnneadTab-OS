#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "NOT IN USE"
__title__ = "72_fix_area_view_title(NOT IN USE)"

from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def fix_area_view_title():
    # get all view on this sheet
    sheets = forms.select_sheets()

    for sheet in sheets:
        for view_id in sheet.GetAllPlacedViews ():
            view = doc.GetElement(view_id)

            title = view.LookupParameter("Title on Sheet").AsString()
            print(title)

            new_title = title.replace("_NoSheet-", "").split("_from")[0].replace("NoSheet", "").replace(")", ") ")
            print(new_title)

            view.LookupParameter("Title on Sheet").Set(new_title)


            # for each view, remove NOSHEET and everything after _from
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    t = DB.Transaction(doc, "fix area title name")
    t.Start()
    fix_area_view_title()
    t.Commit()
