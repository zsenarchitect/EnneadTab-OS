# -*- coding: utf-8 -*-

from EnneadTab import NOTIFICATION


try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = __revit__.ActiveUIDocument
    DOC = UIDOC.Document
    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()

def get_sheet_by_sheet_num( sheet_num, doc = DOC):
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).ToElements()
    
    for sheet in all_sheets:
        if sheet.SheetNumber == sheet_num:
            return sheet
    return None


