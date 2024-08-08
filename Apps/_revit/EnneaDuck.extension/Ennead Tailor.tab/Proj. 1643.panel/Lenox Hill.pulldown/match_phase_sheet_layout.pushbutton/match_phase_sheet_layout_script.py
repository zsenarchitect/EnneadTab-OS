#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Use me to batch align viewports over many sheet. It search the matching rule by detail number, then apply same title offset and title line length. This is built or LHH phasing diagrams and works way better than Ideate for this senario."
__title__ = "Match Phase Sheet Layout"

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
WORK_SHEETS = [
    "PH-02",
    "PH-03",
    "PH-04",
    "PH-05",
    "PH-06",
    "PH-07"
    ]

@ERROR_HANDLE.try_catch_error
def match_phase_sheet_layout():

    t = DB.Transaction(doc, __title__)
    t.Start()
    
    ref_sheet = REVIT_SHEET.get_sheet_by_sheet_num(REF_SHEET)

    data = {}
    title_length = -1
    title_offset = None

    # get the first first viewport as all data source
    for viewport_id in ref_sheet.GetAllViewports():
        viewport = doc.GetElement(viewport_id)
        view = doc.GetElement(viewport.ViewId)
        detail_num = REVIT_VIEW.get_detail_number(view)
        if detail_num == "11":
            title_length = viewport.LabelLineLength
            title_offset = viewport.LabelOffset
            break


            
    # get all viewports in the ref sheet, store each viewport data into a dict.
    # the key is the detail number of the viewport, the value is another set of dict, where it store those data:
    # viewport location, viewport title offset, title length
    for viewport_id in ref_sheet.GetAllViewports():
        viewport = doc.GetElement(viewport_id)
        view = doc.GetElement(viewport.ViewId)
        detail_num = REVIT_VIEW.get_detail_number(view)
        position = viewport.GetBoxCenter()
        viewport.LabelOffset = title_offset
        viewport.LabelLineLength = title_length
            
        data[detail_num] = {
            "position": position,
            "title_offset": title_offset,
            "title_length": title_length
            }





        
    for i, work_sheet in enumerate(WORK_SHEETS):
        sheet = REVIT_SHEET.get_sheet_by_sheet_num(work_sheet)
        for j, viewport_id in enumerate(sheet.GetAllViewports()):
            viewport = doc.GetElement(viewport_id)
            view = doc.GetElement(viewport.ViewId)
            detail_num = REVIT_VIEW.get_detail_number(view)
            if detail_num in data:

                print ("<{}>[{}]: {}, {}".format(i+1, j+1, detail_num, view.Name))
                viewport.SetBoxCenter(data[detail_num]["position"])
                viewport.LabelOffset = data[detail_num]["title_offset"]
                viewport.LabelLineLength = data[detail_num]["title_length"]
            else:
                print ("CANNOT FIND <{}>[{}]: {}, {}".format(i+1, j+1, detail_num, view.Name))
    t.Commit()

    NOTIFICATION.messenger("Finished")


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    match_phase_sheet_layout()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







