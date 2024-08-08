#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Create new sheets based on data from Excel"
__title__ = "Excel Sheet Creator"

# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
        
def get_titleblock_id():
    all_ids = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()
    return filter(lambda x: x.Family.Name == "Consaultant Sheet Placeholder", list(all_ids))[0].Id
            
@EnneadTab.ERROR_HANDLE.try_catch_error()
def excel_sheet_creator():
    pass
    excel_path = r"J:\2306\2_Record\2023-07-31 SD Submission\SD Sheetlist_REV00.xlsx"
    data = EnneadTab.EXCEL.read_data_from_excel(excel_path, worksheet = "Sheet1", by_line = True)
    data = [x for x in data if x[0] == "YES"]
    # print (data)

    titleblock_type_id = get_titleblock_id()
    # print titleblock_type_id
    t = DB.Transaction(doc, __title__)
    t.Start()
    for creation_data in data:
        print (creation_data)
        sheet = DB.ViewSheet.Create(doc, titleblock_type_id)
        
        sheet.SheetNumber = creation_data[4]

        sheet.LookupParameter("Sheet Name").Set(creation_data[6])
        
        sheet.LookupParameter("Sheet_$Group").Set(creation_data[1] + "_" + creation_data[3])
    t.Commit()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    excel_sheet_creator()
    











