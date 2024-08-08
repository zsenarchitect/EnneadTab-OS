#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "layout viewport on sheet based on the phasing and level name"
__title__ = "Phase Diagram Layout update"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SHEET, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


REF_SHEET = "PH-01"
LEVLE_MAP = {
    "B2":1,
    "B1":2,
    "L1":3,
    "L2":4,
    "L3":5,
    "L4":6,
    "L5":7,
    "L6":8,
    "L7":9,
    "L8":10,
    "L9":11,
    "L10":12,
    "L10 MEZZ":13,
    "L11":14,
    "L12":15,
    "L13":16,
    "L14":17,
    "L15":18,
    "L16":19,
    "L17":20,
    "L18":21,
    "L19":22,
    "L20":23,
    "L21 MEP":24,
    "L22 MEP":25
}

def get_all_phase():
    phase_array = doc.Phases
    return list(phase_array)
    all_phase_ids = DB.FilteredElementCollector(doc).OfClass(DB.Phase).ToElementIds ()
    return sorted([ doc.GetElement(phase_id) for phase_id in all_phase_ids], key = lambda x: x.Name)

PHASE_MAP = {phase.Name:i for i, phase in enumerate(get_all_phase(), 1)}
@ERROR_HANDLE.try_catch_error
def match_phase_sheet_layout():

    sheet = REVIT_SHEET.get_sheet_by_sheet_num(REF_SHEET)
        
    t = DB.Transaction(doc, __title__)
    t.Start()

    for j, viewport_id in enumerate(sheet.GetAllViewports()):
        viewport = doc.GetElement(viewport_id)
        view = doc.GetElement(viewport.ViewId)
        REVIT_VIEW.set_detail_number(view, "____temp{}".format(j))

    for j, viewport_id in enumerate(sheet.GetAllViewports()):
        viewport = doc.GetElement(viewport_id)
        view = doc.GetElement(viewport.ViewId)
        # factor, old_detail_num, _, _ = view.Name.split("_")
        # factor = int(factor[-1])
        # old_detail_num = int(old_detail_num)

        # interval = 40 if factor<= 5 else 30
        # new_detail_num = old_detail_num + (factor-1)*interval

        # REVIT_VIEW.set_detail_number(view, new_detail_num)


        row, column = LEVLE_MAP[view.GenLevel.Name], PHASE_MAP[doc.GetElement(view.LookupParameter("Phase").AsElementId()).Name]
        detail_num = "{}@{}".format(str(row).zfill(2), column)

        REVIT_VIEW.set_detail_number(view, detail_num)
        REVIT_VIEW.set_view_title(view, "{}_{}".format(view.GenLevel.Name, doc.GetElement(view.LookupParameter("Phase").AsElementId()).Name))

        # print (detail_num)

        # print (row, column)

        viewport.SetBoxCenter(DB.XYZ(column * 1.5, row * 0.8, 0))
        viewport.LabelOffset = DB.XYZ(0.1, -0.05, 0)
        viewport.LabelLineLength = 0.1

        # print ("\n\n")


    t.Commit()

    NOTIFICATION.messenger("Finished")


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    match_phase_sheet_layout()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







