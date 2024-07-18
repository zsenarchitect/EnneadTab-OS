#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """Are you having trouble trusting the excel when it is past to you from someone else? What if the formula is incorrect and is citing the wrong cell? You could not know it unless you click each one of the cell and see if there is a hidden formula. 
Now this formula checker will help you find every hidden formula so you can see for yourself.
It highlight the cells as dash."""
__title__ = "Inspect Excel\nFormula"
__tip__ = True
from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
from EnneadTab import ERROR_HANDLE, EXCEL, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error()
def check_formula():

    excel = forms.pick_excel_file()
    if not excel:
        return
    # if excel.endswith(".xlsx"):
    #     NOTIFICATION.messenger("Please saveas .xls")
    sheets = EXCEL.get_all_worksheets(excel)
    sheet = forms.SelectFromList.show(sheets, button_name="Select WorkSheet", multiselect=False, title="Which worksheet to check??")
    EXCEL.check_formula(excel, sheet)
    pass

    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
    NOTIFICATION.messenger("Done! All formula printed!\nAll formula cell are highlighted in dash border in a local copy.")


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    check_formula()
    







