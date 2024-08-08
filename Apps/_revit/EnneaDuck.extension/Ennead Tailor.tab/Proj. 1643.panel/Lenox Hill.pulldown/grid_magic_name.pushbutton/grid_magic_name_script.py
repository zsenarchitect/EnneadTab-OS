#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "grid_magic_name"

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
def grid_magic_name(doc):
    return
    all_grids = DB.FilteredElementCollector(doc).OfClass(DB.Grid).ToElements()

    all_grid_types = DB.FilteredElementCollector(doc).OfClass(DB.GridType).ToElements()
    for grid_type in all_grid_types:
        if grid_type.LookupParameter("Type Name").AsString() == "Primary":
            primary_grid_type_id = grid_type.Id
        if grid_type.LookupParameter("Type Name").AsString() == "Secondary":
            secondary_grid_type_id = grid_type.Id



    t = DB.Transaction(doc, __title__)
    t.Start()

    for grid in all_grids:
        try:
            grid.Name = grid.Name.replace("t", "", 1).replace("p", "", 1)
        except:
            pass
        
        grid_name_intent = grid.Name.replace("t", "", 1).replace("p", "", 1) # max replace 1
        if "_" in grid_name_intent:
            grid_name_intent = grid_name_intent.split("_")[0]

        if "." not in grid_name_intent:
            # this is a primary type
            grid.LookupParameter("FormatName").Set(grid_name_intent)
            grid.LookupParameter("PrimaryIndex").Set(grid_name_intent)
            grid.LookupParameter("SecondaryIndex").Set("~")
            grid.ChangeTypeId(primary_grid_type_id)
            
        else:
            # this is a secondary type that looks like X.x
            grid.LookupParameter("FormatName").Set(grid_name_intent)
            primary_name, secondary_name = grid_name_intent.split(".")
            grid.LookupParameter("PrimaryIndex").Set(primary_name)
            grid.LookupParameter("SecondaryIndex").Set("."+secondary_name)
            grid.ChangeTypeId(secondary_grid_type_id)
    
    t.Commit()



################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    grid_magic_name(doc)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







