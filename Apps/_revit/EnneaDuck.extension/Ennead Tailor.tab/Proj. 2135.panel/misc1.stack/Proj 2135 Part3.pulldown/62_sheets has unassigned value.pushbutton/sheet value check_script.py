#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Check esential sheet value has been assigned."
__title__ = "62_check sheet value"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def check_default_value(correct_error = True):
    key_para = "EA_INTERNAL PRINT"
    key_para = "Print_In_Color"
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    all_sheets = list(all_sheets)
    all_sheets.sort(key = lambda x: x.SheetNumber)
    for sheet in all_sheets:
        para = sheet.LookupParameter(key_para)
        if EA_UTILITY.parameter_has_unassigned_value(para):
            print("not assigned Print In Color value at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
            if correct_error:
                para.Set(0)

        if not sheet.LookupParameter("Appears In Sheet List").AsInteger():
            sheet.LookupParameter("Appears In Sheet List").Set(1)
            sheet.LookupParameter("Sheet Note").Set("Internal")
            print("force 'appear in sheet list' turn on and assign 'internal' sheet note at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))



        if sheet.LookupParameter("Sheet Note").AsString() == "DD":
            print("sheet note as 'DD' at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
            sheet.LookupParameter("Sheet Note").Set("Internal")

        if "SK" in sheet.SheetNumber:
            print("sheet SK at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
            sheet.LookupParameter("Sheet Note").Set("Internal")
            sheet.LookupParameter("Sheet_$Order").Set(-5)

        if "P-" == sheet.SheetNumber[0:2]:
            print("sheet presentation at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
            sheet.LookupParameter("Sheet Note").Set("Internal")
            sheet.LookupParameter("Sheet_$Order").Set(-10)

        if "X" == sheet.SheetNumber[0]:
            print("sheet X at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
            sheet.LookupParameter("Sheet Note").Set("Internal")
            sheet.LookupParameter("Sheet_$Order").Set(-20)

        if sheet.LookupParameter("Sheet Note").AsString() == r"NOT ISSUE for 05/27":
            print("sheet note as 'not issue for 05/27' at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
            sheet.LookupParameter("Sheet Note").Set("Internal")

        if sheet.LookupParameter("Sheet_$Group").AsString() in ["02_DD_Documentation", "02_SD_Documentation"]:
            print("changing DD folder and SD folder to basic document folder at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
            sheet.LookupParameter("Sheet_$Group").Set("02_Documentation")

        issues = ["Issue 2022/09/23", "Issue 2022/09/29"]
        #if sheet.SheetNumber == "A-N3-328":
            #print "AAAAAAA"
        for issue in issues:
            issue_para = sheet.LookupParameter(issue)
            if not issue_para:
                continue

            if issue_para.AsString() == u"\u25A0":
                if sheet.LookupParameter("Sheet Note").AsString() == "Internal":
                    print("remove internal note for sheet that will print at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
                    sheet.LookupParameter("Sheet Note").Set("")
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    docs = EA_UTILITY.select_top_level_docs()
    for doc in docs:
        print("\n\n------------------- working on doc: " + doc.Title)
        t = DB.Transaction(doc, "fix unassigned value")
        t.Start()
        check_default_value()
        t.Commit()

    print("\n\n####### Tool finish")
