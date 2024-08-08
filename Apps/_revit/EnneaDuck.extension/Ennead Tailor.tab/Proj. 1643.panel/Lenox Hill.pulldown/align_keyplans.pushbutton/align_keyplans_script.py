#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Align all keyplan to one source location viewpotty."
__title__ = "Align Key Plams"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION, REVIT_SHEET, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


KEY_PLAN_REF = "PS 1_A115_1_L14 LACHMAN PENT ROOF"
MAIN_PLAN_REF = "PS 1_A115_10_L14 LACHMAN PENT ROOF"
WORK_SHEET = REVIT_SHEET.get_sheet_by_sheet_num("PS 1_A115")


@ERROR_HANDLE.try_catch_error
def align_key_plans():
    align_plan(KEY_PLAN_REF, WORK_SHEET)
    print ("#######################################")
    align_plan(MAIN_PLAN_REF, WORK_SHEET)


def align_plan(ref_view, work_sheet):
    t = DB.Transaction(doc, __title__)
    t.Start()
    




    # get the first first viewport as all data source
    for viewport_id in work_sheet.GetAllViewports():
        viewport = doc.GetElement(viewport_id)
        view = doc.GetElement(viewport.ViewId)
        if view.Name == ref_view:
            viewport.ViewportPositioning = DB.ViewportPositioning.ViewOrigin
            position = viewport.GetBoxCenter()
            scale = view.Scale

            break



    all_raw_sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).ToElements()
    all_sheets = REVIT_SELECTION.filter_elements_changable(all_raw_sheets)
    for sheet in sorted(list(set(all_raw_sheets)-set(all_sheets)), key = lambda x: x.SheetNumber):
        print ("skip: " + sheet.SheetNumber)
        
    for i, sheet in enumerate(all_sheets):

        
        for j, viewport_id in enumerate(sheet.GetAllViewports()):
            viewport = doc.GetElement(viewport_id)
            view = doc.GetElement(viewport.ViewId)
            if view.Name == ref_view:
                continue

            if view.Scale == scale:
                viewport.ViewportPositioning = DB.ViewportPositioning.ViewOrigin
                viewport.SetBoxCenter(position)
                print ("align: " + sheet.SheetNumber)

    t.Commit()

    NOTIFICATION.messenger("Finished")


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    align_key_plans()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







