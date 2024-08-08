#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "update_delta_area_graphic"

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
def update_delta_area_graphic(doc, show_log = True):
    pass

    # safe read excel to get the number and get a dict for each ref number should have area

    
    # get all the related areas
    areas = get_areas()


    

    # iterate the areas:
    # -what is he cureent area, lookup the ref num in dict for what it should be
    # -if the cureent area less than to the ref num designed SF, find the data block that has ref num and put in the delta for "area cannot fit"
    # - if the cureent area is greater than the ref num designed SF, find the data block that has ref num and put in the delta for "assigned too much!"
    # when cannot find the data block, create one in new dump draft view and active that view
    # when there are ref num not in the dict, notify user and continue
    for area in areas:
        print(area.Area)

    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """

def get_areas():
    areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    return [x for x in areas if x.AreaScheme.Name == "abcdef"]
################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    update_delta_area_graphic(doc)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







