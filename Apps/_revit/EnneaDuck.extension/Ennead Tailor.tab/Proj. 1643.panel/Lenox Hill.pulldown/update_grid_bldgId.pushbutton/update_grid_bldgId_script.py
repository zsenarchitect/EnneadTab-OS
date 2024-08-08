#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "update_grid_bldgId"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error
def update_grid_bldgId(doc):
    all_grids = DB.FilteredElementCollector(doc).OfClass(DB.Grid).ToElements()


    t = DB.Transaction(doc, __title__)
    t.Start()
    for grid in all_grids:
        scopebox = doc.GetElement(grid.LookupParameter("Scope Box").AsElementId())
        try:
            bldg_id = scopebox.Name
        except:
            bldg_id = "None"
        grid.LookupParameter("BldgId").Set(bldg_id)
    t.Commit()



################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    update_grid_bldgId(doc)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







