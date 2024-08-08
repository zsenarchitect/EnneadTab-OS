#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Make sure all sheet names and view names are capped."
__title__ = "All Cap Sheet Name and View Name"

# from pyrevit import forms #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def all_cap_sheet_name():
    t = DB.Transaction(doc, __title__)
    t.Start()
    for sheet in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements():
        # make sheet name upper case
        sheet.Name = sheet.Name.upper()
        for viewId in sheet.GetAllPlacedViews():
            view = doc.GetElement(viewId)
            view.Name = view.Name.upper()

    t.Commit()

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    all_cap_sheet_name()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)












