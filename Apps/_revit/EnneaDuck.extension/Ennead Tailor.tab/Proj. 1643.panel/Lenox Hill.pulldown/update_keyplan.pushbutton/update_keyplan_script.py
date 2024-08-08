#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Auto pick keyplan based on the first doc view phase"
__title__ = "Update Keyplan"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error
def update_keyplan(doc):
    titleblocks = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().ToElements()
    titleblocks = REVIT_SELECTION.filter_elements_changable(titleblocks)
    titleblock_dict = {titleblock.LookupParameter("Sheet Number").AsString(): titleblock for titleblock in titleblocks}

    all_sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).ToElements()
    all_sheets = REVIT_SELECTION.filter_elements_changable(all_sheets)

    if not all_sheets:
        return



    t = DB.Transaction(doc, __title__)
    t.Start()
    
    for sheet in all_sheets:
        for view_id in sheet.GetAllPlacedViews():
            view = doc.GetElement(view_id)
            if view.ViewType in [
                DB.ViewType.FloorPlan,
                DB.ViewType.CeilingPlan,
                DB.ViewType.AreaPlan,
                DB.ViewType.Elevation,
                DB.ViewType.Detail,
                DB.ViewType.Section,
                DB.ViewType.ThreeD
                ]:
                break
        else:
            continue

        
        phase_name = doc.GetElement(view.LookupParameter("Phase").AsElementId()).Name
        titleblock = titleblock_dict.get(sheet.SheetNumber)
        if not titleblock:
            continue
        
        for para_index in range(8):
            para_name = "Set {}".format(para_index + 1)
            para = titleblock.LookupParameter(para_name)
            if not para:
                continue

            if para_name == phase_name:
                para.Set(1)
            else:
                para.Set(0)



    t.Commit()



################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    update_keyplan(doc)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







