#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "For DOB submission in NYC there reuqires a page number on the titleblock."
__title__ = "Update DOB\nPage Number"

# from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, NOTIFICATION, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def update_DOB_page(doc, show_log = True):
    all_link_docs = REVIT_APPLICATION.get_revit_link_docs(link_only = True)
    all_link_docs.append(doc)
    all_sheets = []
    for working_doc in all_link_docs:
        
        all_working_sheets = list(DB.FilteredElementCollector(working_doc).OfCategory(DB.BuiltInCategory.OST_Sheets).ToElements())
        
        for sheet in all_working_sheets:
            if not sheet.LookupParameter("Sheet_$Issue_DOB"):
                if show_log:
                    NOTIFICATION.messenger("Need proper parameter for your DOB marking in doc [{}].\nAsk Gayatri for detail.".format(working_doc.Title))
                return

            if not sheet.LookupParameter("Sheet No.") or not sheet.LookupParameter("Total Sheets"):
                NOTIFICATION.messenger("Need proper parameter for your DOB page numbering in doc [{}].\nAsk Gayatri for detail.".format(working_doc.Title))
                return

        all_sheets.extend(all_working_sheets)

    good_sheets = [s for s in all_sheets if s.LookupParameter("Sheet_$Issue_DOB").AsString() != ""  and s.LookupParameter("Sheet_$Issue_DOB").HasValue]
    bad_sheets = [s for s in all_sheets if s not in good_sheets]
    good_sheets.sort(key = lambda x: "{}_{}_{}".format(x.LookupParameter("Sheet_$Group").AsString(),
                                                       x.LookupParameter("Sheet_$Series").AsString(),
                                                       x.SheetNumber))
    print( good_sheets)
    t = DB.Transaction(doc, __title__)
    t.Start()
    for i, sheet in enumerate(good_sheets):
        if not REVIT_SELECTION.is_changable(sheet):
            print ("{} DOB page number not changed becasue {} is owning it.".format(sheet.SheetNumber, REVIT_SELECTION.get_owner(sheet)))
            continue
        sheet.LookupParameter("Sheet No.").Set(i+1)
        sheet.LookupParameter("Total Sheets").Set(len(good_sheets))

    for sheet in bad_sheets:
        sheet.LookupParameter("Sheet No.").Set(-1)
        sheet.LookupParameter("Total Sheets").Set(-1)
    t.Commit()

    if show_log:
        NOTIFICATION.messenger("Update DOB page number done.")


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    update_DOB_page(doc)
    







