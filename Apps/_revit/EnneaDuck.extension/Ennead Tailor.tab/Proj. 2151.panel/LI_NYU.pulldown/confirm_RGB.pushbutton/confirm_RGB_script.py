#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Even when you type in the RGB value in excel, that might get changed by someone in the future and cannot be trusted. I suggest to NOT include RGB value in the excel so there is only one source of truth, but if the team REALLY nned to have RGB value in excel written out, run this to confirm the color of cell is matching the number in excel"
__title__ = "Confirm RGB"

# from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

from EnneadTab import EXCEL

from EnneadTab.EXCEL import ExcelDataItem


EXCEL_PATH = "J:\\2151\\2_Master File\\B-70_Programming\\03_Colors\\Color Scheme_NYULI_Active.xls"
OUT_EXCEL_PATH = "J:\\2151\\2_Master File\\B-70_Programming\\03_Colors\\archive\\temp_out.xls"


        
@ERROR_HANDLE.try_catch_error()
def confirm_RGB(doc, show_log = False):
    flag = False
    raw_data = EXCEL.read_data_from_excel(EXCEL_PATH, 
                                            worksheet = "HEALTHCARE", 
                                            return_dict=True)

    new_data = []
    for pointer in raw_data:
        row_flag = False
        i,j = pointer # i = row, j = column
        if j != 3: 
            continue
        
        if i <=2:
            # ignore first two row, those rowsa re reserved for notes and header
            continue
        
        
        pointer_right_right = (i, j+2)
        subject_color = raw_data[pointer_right_right].get("color")
        
        # skip row where color is not defined(maybe due to merged cell), only record by row that define.
        if subject_color is None:
            continue
        

        new_data.append(ExcelDataItem(str(raw_data[(i, j)].get("value")), i, j+2))
        try:

            manual_R = raw_data[(i, j+3)].get("value")

            if isinstance(manual_R, str):
                manual_R = int(manual_R.replace("R:", "").strip())
            else:
                manual_R = int(manual_R)

            if manual_R-subject_color[0] != 0:
                flag = True
                row_flag = True
            new_data.append(ExcelDataItem(manual_R,i, j+3))
            new_data.append(ExcelDataItem(subject_color[0],i, j+4))
            new_data.append(ExcelDataItem(manual_R-subject_color[0], i, j+5))
            
            
            manual_G = raw_data[(i, j+4)].get("value")
            if isinstance(manual_G, str):
                manual_G = int(manual_G.replace("G:", "").strip())
            else:
                manual_G = int(manual_G)
            if manual_G-subject_color[1] != 0:
                flag = True
                row_flag = True
            new_data.append(ExcelDataItem(manual_G, i, j+6))
            new_data.append(ExcelDataItem(subject_color[1], i, j+7))
            new_data.append(ExcelDataItem(manual_G-subject_color[1], i, j+8))
            
            
            manual_B = raw_data[(i, j+5)].get("value")
            if isinstance(manual_B, str):
                manual_B = int(manual_B.replace("B:", "").strip())
            else:
                manual_B = int(manual_B)
            if manual_B-subject_color[2] != 0:
                flag = True
                row_flag = True
            new_data.append(ExcelDataItem(manual_B, i, j+9))
            new_data.append(ExcelDataItem(subject_color[2], i, j+10))
            new_data.append(ExcelDataItem(manual_B-subject_color[2], i, j+11))
        except Exception as e:
            # print (traceback.format_exc())
            pass

        if row_flag:
            new_data.append(ExcelDataItem("Value Mismatch!!",i, j))
        
    new_data.append(ExcelDataItem("The R you type in", 2, j+5))
    new_data.append(ExcelDataItem("The R you get from color cell", 2, j+6))
    new_data.append(ExcelDataItem("The R difference", 2, j+7))
    new_data.append(ExcelDataItem("The G you type in", 2, j+8))
    new_data.append(ExcelDataItem("The G you get from color cell", 2, j+9))
    new_data.append(ExcelDataItem("The G difference", 2, j+10))
    new_data.append(ExcelDataItem("The B you type in", 2, j+11))
    new_data.append(ExcelDataItem("The B you get from color cell", 2, j+12))
    new_data.append(ExcelDataItem("The B difference", 2, j+13))


    EXCEL.save_data_to_excel(new_data, OUT_EXCEL_PATH, worksheet = "HEALTHCARE", open_after = flag)

    if flag:
        NOTIFICATION.messenger("Please correct the RGB value you have typed in. It is no longer the same as the excel cell color.")
    else:
        NOTIFICATION.messenger("No mismatch found. Your RGB value is all correctly written.")

################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    confirm_RGB(doc, show_log = True)
    







