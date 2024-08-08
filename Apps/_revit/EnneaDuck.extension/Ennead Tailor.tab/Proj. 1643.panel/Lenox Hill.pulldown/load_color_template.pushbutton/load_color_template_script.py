#!/usr/bin/python
# -*- coding: utf-8 -*-


__doc__ = """Update color scheme with office template excel version
J:\\1643\\2_Master File\\B-70_Programming\\01_Program & Analysis\\2024-04-11 Color Scheme_LHH.xls.
NOTE: excel should be saved with .xls instead of .xlsx format
Also note, the column header should be as such:
A: Department(Section Name)
B: Department Abbr.
C: Department Color

D: Program(SubSection Name)
E: Program Abbr.
F: Program Color

ANYTHING ELSE IN THE EXCEL FILE WILL BE IGNORED, including the hex code text on color cell and red, green, blue value number. 
Those manual color text cannot be trusted on the long run.
"""
__title__ = "Load Color Template"

# from pyrevit import forms #
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_COLOR_SCHEME
from pyrevit import script #



from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore



EXCEL_PATH = "J:\\1643\\2_Master File\\B-70_Programming\\01_Program & Analysis\\2024-05-07 Color Scheme_LHH.xls"
NAMING_MAP = {"department_color_map":"Section Category",
              "program_color_map":"SubSection Category"}



    
@ERROR_HANDLE.try_catch_error()
def load_color_template():
    REVIT_COLOR_SCHEME.load_color_template(doc, NAMING_MAP, EXCEL_PATH, is_remove_bad = False)
    


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    load_color_template()









