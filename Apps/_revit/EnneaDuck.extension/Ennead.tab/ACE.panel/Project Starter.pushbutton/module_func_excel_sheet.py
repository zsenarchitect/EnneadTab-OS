#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyrevit import forms #

from EnneadTab import EXE, EXCEL, FOLDER, ERROR_HANDLE, ENVIRONMENT
from Autodesk.Revit import DB # pyright: ignore 

def is_new_sheet_number_ok(doc, new_sheet_numbers):       
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    all_sheet_numbers = [x.SheetNumber for x in all_sheets]
    
    # get the intersection between the new sheet numbers and the existing sheet numbers
    # if the intersection is empty, then the new sheet numbers are all unique
    intersection = set(new_sheet_numbers) & set(all_sheet_numbers)
    
    if intersection:
        print ("The following sheet numbers are already in use: {}".format(intersection))

        return False
    return True
    

     
@ERROR_HANDLE.try_catch_error()
def excel_sheet_creator(doc, excel_path, worksheet_name , data_map):

    
    data = EXCEL.read_data_from_excel(excel_path, worksheet = worksheet_name, by_line = True)
    data = [x for x in data if x[0] == "YES"]
    # print (data)
    new_sheet_numbers = [x[4] for x in data]
    if not is_new_sheet_number_ok(doc, new_sheet_numbers):
        return

    titleblock_type_id = forms.select_titleblocks(title = "Pick the titleblock that will be used for the new sheets.",
                                                  doc = doc)
    if not titleblock_type_id:
        return
    
    # print titleblock_type_id
    t = DB.Transaction(doc, "Create Sheets from Excel")
    t.Start()
    for i,creation_data in enumerate(data):
        sheet = DB.ViewSheet.Create(doc, titleblock_type_id)
        
        try:
            sheet.SheetNumber = creation_data[data_map["sheet_number"]]
        except Exception as e:
            print (e)
            sheet.SheetNumber = creation_data[data_map["sheet_number"]] + "_conflict"
            pass
        
        sheet_name = creation_data[data_map["sheet_name"]]
        sheet.LookupParameter("Sheet Name").Set(sheet_name)
        print ("{}/{}: Creating {}:{}".format(i, len(data), sheet.SheetNumber, sheet_name))
        
        try:
            sheet.LookupParameter("MC_$Translate").Set(creation_data[data_map["translation"]])
        except:
            pass
        try:
            sheet.LookupParameter("Sheet_$Group").Set(creation_data[data_map["sheet_group"]])
        except:
            pass
        
    t.Commit()



@ERROR_HANDLE.try_catch_error()
def open_sample_excel():
    excel_path = "{}\ENNEAD.extension\Ennead.tab\ACE.panel\Project Starter.pushbutton\Make Sheet With Excel.xls".format(ENVIRONMENT.REVIT_HOST_FOLDER)
    copy = FOLDER.copy_file_to_local_dump_folder(excel_path,
                                                           "Sample Sheet Creation Data.xls")
    EXE.open_file_in_default_application(copy)
    


if __name__== "__main__":
    pass

