#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Create new sheets based on data from Excel.\nIf you need help on what kind of Excel to prepare, you can open a sample excel and begin from there."
__title__ = "Create Sheets\nBy Excel"
__tip__ = True
from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_APPLICATION, LOG
from EnneadTab import NOTIFICATION, ERROR_HANDLE, EXCEL
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
        


def is_new_sheet_number_ok(new_sheet_numbers):       
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    all_sheet_numbers = [x.SheetNumber for x in all_sheets]
    
    # get the intersection between the new sheet numbers and the existing sheet numbers
    # if the intersection is empty, then the new sheet numbers are all unique
    intersection = set(new_sheet_numbers) & set(all_sheet_numbers)
    
    if intersection:
        print ("The following sheet numbers are already in use: {}".format(intersection))

        return False
    return True
    

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def excel_sheet_creator():
    excel_path = forms.pick_excel_file(title="Where is the excel thjat has the new sheet data?")   
    # this is the sample excel for reference. 
    # excel_path = r"J:\2306\2_Record\2023-07-31 SD Submission\SD Sheetlist_REV00.xlsx"
    
    data = EXCEL.read_data_from_excel(excel_path, worksheet = "Sheet1", by_line = True)
    if not data:
        NOTIFICATION.messenger(main_text = "Cannot open this excel")
        return
    if not data.endswith(".xlsx"):
        NOTIFICATION.messenger(main_text = "need .xlsx file")
        return
    data = [x for x in data if x[0] == "YES"]
    # print (data)
    new_sheet_numbers = [x[4] for x in data]
    if not is_new_sheet_number_ok(new_sheet_numbers):
        return

    titleblock_type_id = forms.select_titleblocks(title = "Pick the titleblock that will be used for the new sheets.")
    if not titleblock_type_id:
        return
    
    # print titleblock_type_id
    t = DB.Transaction(doc, __title__)
    t.Start()
    for creation_data in data:
        print (creation_data)
        sheet = DB.ViewSheet.Create(doc, titleblock_type_id)
        
        sheet.SheetNumber = creation_data[4]

        sheet.LookupParameter("Sheet Name").Set(creation_data[6])
        try:
            sheet.LookupParameter("Sheet_$Group").Set(creation_data[1] + "_" + creation_data[3])
        except:
            pass
    t.Commit()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    excel_sheet_creator()
    











