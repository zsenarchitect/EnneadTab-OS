#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Export and open schedule in excel."
__title__ = "Schedule2Excel"
__tip__ = True

import csv
from pyrevit import forms 
from pyrevit import script, revit
import os
import xlsxwriter
import csv
import re
import ENNEAD_LOG

from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
from EnneadTab.REVIT import REVIT_FORMS
            
@ERROR_HANDLE.try_catch_error
def schedule2excel():

    schedules = forms.select_schedules()

    if not schedules: return

    basefolder = forms.pick_folder()
    export_option = DB.ViewScheduleExportOptions()

    opts = ["Export the column headers only.",
            "Both column headers and grouped header cells are exported."]

    res = REVIT_FORMS.dialogue(main_text="How to export the header?",
                               options=opts)
    if res == opts[0]:
        export_option.ColumnHeaders = DB.ExportColumnHeaders.OneRow
    elif res == opts[1]:
        export_option.ColumnHeaders = DB.ExportColumnHeaders.MultipleRows
    else:
        return
    export_option.TextQualifier = DB.ExportTextQualifier.DoubleQuote

    # determine which separator to use
    csv_sp = ','
    

    export_option.FieldDelimiter = csv_sp
    export_option.Title = False


    opts = [["Yes", "Preserve visual as much as to revit."],
        ["No", "More usful for manipulation"]]
    res = REVIT_FORMS.dialogue(main_text="Whether to export group headers, footers, and blank lines",
                               options=opts)
    if res == opts[0][0]:
        export_option.HeadersFootersBlanks = True
    elif res == opts[1][0]:
        export_option.HeadersFootersBlanks = False
    else:
        return
    

    for schedule in schedules:
        file_name = re.sub(r'[\/:*?"<>|]', '', schedule.Name) + '.csv'
        
        schedule.Export(basefolder, file_name, export_option)
        exported_csv = os.path.join(basefolder, file_name)
        revit.files.correct_text_encoding(exported_csv)

        excel = convert_csv2excel(exported_csv)
        

        os.startfile(excel)

def convert_csv2excel(csv_file_path):


    excel_file_path = csv_file_path.replace(".csv", ".xlsx")
    # Create an Excel workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(excel_file_path)
    worksheet = workbook.add_worksheet()

    # Open the CSV file and read its rows.
    with open(csv_file_path, 'rb') as csvfile:  # Use 'rb' mode for Python 2
        reader = csv.reader(csvfile)
        for row_index, row in enumerate(reader):
            for column_index, cell in enumerate(row):
                worksheet.write(row_index, column_index, cell)

    # Close the Excel file.
    workbook.close()

    return excel_file_path


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    schedule2excel()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







