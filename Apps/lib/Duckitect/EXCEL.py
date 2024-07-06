#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
try:
    # 设定了输出的环境为utf8
    sys.setdefaultencoding('utf-8')
except:
    pass


import ENVIRONMENT
import EXE
import NOTIFICATION
import COLOR
import FOLDER 
sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER)
import xlrd
import xlsxwriter



def letter_to_index(letter):
    return ord(letter.upper()) - ord('A')

def get_column_index(letter):
    return letter_to_index(letter)

class ExcelDataItem():
    def __init__(self, item, row, column, cell_color = None, text_color = None, border_style = None, border_color = None ):
        if isinstance(column, str):
            column = letter_to_index(column)
        self.item = item
        self.row = row
        self.column = column
        self.cell_color = cell_color
        self.text_color = text_color
        self.border_style = border_style
        self.border_color = border_color

    def __str__(self):
        info = "ExcelDataItem: {} @ ({}, {})".format(self.item, self.row, self.column)
        if self.cell_color:
            info += " ({})".format(self.cell_color)
        return info


def get_all_worksheets(filepath):

    wb = xlrd.open_workbook(filepath, on_demand=True)
    return wb.sheet_names()

def read_data_from_excel(filepath, worksheet = None, by_line = True, return_dict=False):


    wb = xlrd.open_workbook(filepath,formatting_info=return_dict)#, encoding_override = "cp1252")#""big5")#"iso2022_jp_2")#"gb18030")#"gbk")#"hz")  #"gb2312")   #"utf8"
    try:
        if not worksheet:
            worksheet = wb.sheet_names()[0]
        sheet = wb.sheet_by_name(worksheet)
    except:
        
        NOTIFICATION.messenger(main_text = "Cannot open worksheet: {}".format(worksheet))
        return None
    #print sheet.cell_value(2, 1)
    
    
    if not return_dict:
    
        OUT = []

        for i in range(0, sheet.nrows):
            OUT.append(sheet.row_values(i))
        return OUT
    
    
    # from collections import OrderedDict
    # OUT = OrderedDict()
    
    
    # OUT = {}
    # for i in range(0, sheet.nrows):
    #     for j in range(sheet.ncols):
    #         cell = sheet.cell(i, j)
    #         text_value = cell.value
            

    #         # Get color
    #         xf_index = sheet.cell_xf_index(i, j)
    #         xf = wb.xf_list[xf_index]
    #         bgx = xf.background.pattern_colour_index
    #         rgb = wb.colour_map.get(bgx) 

    #         # Store in dictionary
    #         OUT[(i, j)] = {'value': text_value, 'color': rgb}
    #         # if i == 2:
    #         #     print (OUT[(i, j)])
            
    # return OUT
    
    
    import clr # pyright: ignore
    clr.AddReference("Microsoft.Office.Interop.Excel")
    from Microsoft.Office.Interop import Excel # pyright: ignore
    excel_app = Excel.ApplicationClass()
    excel_app.Visible = False

    workbook = excel_app.Workbooks.Open(filepath)
    sheet = workbook.Sheets[worksheet]
    
    import COLOR
    OUT = {}
    for i in range(1, sheet.UsedRange.Rows.Count + 1):
        for j in range(1, sheet.UsedRange.Columns.Count + 1):
            cell = sheet.Cells[i, j]
            decimal_color = cell.Interior.Color
            rgb_color = COLOR.decimal_to_rgb(decimal_color)
            cell_value = cell.Value2 if cell.Value2 is not None else ""
            
            # note to self, use i-1 and j-1 becaome the index starting method is different for clr called method
            OUT[(i-1, j-1)] = {'value': cell_value, 'color': rgb_color}
            
            
    workbook.Close(False)
    excel_app.Quit()
    # print OUT

    return OUT



def save_data_to_excel(data, filepath, worksheet = "Duckitect", open_after = True):
    """_summary_

    Args:
        data (list): list of Excel Data item that has row, column, item attr.
        the order is handled before the data entry
        
        
        filepath (_type_): _description_
        worksheet (str, optional): _description_. Defaults to "Duckitect".
        open_after (bool, optional): _description_. Defaults to True.
    """
    # note to self: rework the format method in dataitem so can construct any combonation format
    # see doc here: https://xlsxwriter.readthedocs.io/format.html#format-set-border
    def write_data_item(worksheet, data):

        if any(data.cell_color, data.text_color, data.border_style, data.border_color):
            format_dict = {}
            if data.cell_color:
                format_dict['bg_color'] = COLOR.rgb_to_hex(data.cell_color)
            if data.text_color:
                format_dict['color'] = COLOR.rgb_to_hex(data.text_color)
            if data.border_style:
                format_dict['border'] = data.border_style
            if data.border_color:
                format_dict['border_color'] = COLOR.rgb_to_hex(data.border_color)
            format = workbook.add_format(format_dict)
            worksheet.write(data.row,
                            data.column,
                            data.item,
                            format)
        else:
            worksheet.write(data.row,
                            data.column,
                            data.item)

        # if data.cell_color:
        #     hex_color = COLOR.rgb_to_hex(data.cell_color)
        #     format = workbook.add_format({'bg_color' : hex_color})
        #     worksheet.write(data.row,
        #                     data.column,
        #                     data.item,
        #                     format)
        # elif data.text_color:
        #     hex_color = COLOR.rgb_to_hex(data.text_color)
        #     format = workbook.add_format({'color' : hex_color})
        #     worksheet.write(data.row,
        #                     data.column,
        #                     data.item,
        #                     format)

        # else:
        #     worksheet.write(data.row,
        #                     data.column,
        #                     data.item)

    workbook = xlsxwriter.Workbook(filepath)


    worksheet = workbook.add_worksheet(worksheet)
    for data_entry in data:
        write_data_item(worksheet, data_entry)


    column_max_width_dict = dict()
    for entry in data:
        column, item = entry.column, entry.item
        if column not in column_max_width_dict.keys():
            column_max_width_dict[column] = 0
        column_max_width_dict[column] = max(column_max_width_dict[column], 1.2 * len(str(item)))

    for column in column_max_width_dict.keys():
        worksheet.set_column(column,column , column_max_width_dict[column])



    try:
        workbook.close()
        if not open_after:
            NOTIFICATION.messenger(main_text = "Excel saved at '{}'".format(filepath))
    except:
        NOTIFICATION.messenger(main_text = "the excel file you picked is still open, cannot override. Writing cancelled.")
        return

    if open_after:
        EXE.open_file_in_default_application(filepath)


def unit_test():
    return
    import xlrd
    import WEB

    # Replace this with your SharePoint URL
    sharepoint_url = "https://enneadarch-my.sharepoint.com/:x:/g/personal/scott_mackenzie_ennead_com/Eey-gTYaVIdGuU9Jg65gig8BIUBmc32Aie-0nNsjVSgUfQ?rtime=4PY2woUX3Eg"

    # Open the Excel file from the URL
    str = WEB.get_request(sharepoint_url)
    print (str)
    workbook = xlrd.open_workbook(file_contents=str)

    # Select the first sheet (you can change the sheet index as needed)
    sheet = workbook.sheet_by_index(0)

    # Iterate through rows and print each row
    for row_num in range(sheet.nrows):
        row = sheet.row_values(row_num)
        print(row)

def check_formula(excel, worksheet, highlight_formula = True):
    # find all the cells with formula and print the formula like this:
    # B2 = A2 *1.4 + D4:D12
    # Open the workbook and select the first sheet
    import clr # pyright: ignore
    clr.AddReference("Microsoft.Office.Interop.Excel")
    from Microsoft.Office.Interop import Excel # pyright: ignore
    excel_app = Excel.ApplicationClass()
    excel_app.Visible = False

    excel = FOLDER.copy_file_to_local_dump_folder(excel, "LocalCopy_" + excel)
    workbook = excel_app.Workbooks.Open(excel)
    sheet = workbook.Sheets[worksheet]
    
    for col in range(1, sheet.UsedRange.Columns.Count + 1):
        for row in range(1, sheet.UsedRange.Rows.Count + 1): 
            cell = sheet.Cells(row, col)
            # Check if there's a formula in the cell
            if cell.HasFormula:
                # Print the location and the formula
                cell_value = cell.Value2 if cell.Value2 is not None else ""
                print('cell[{}{}] = {} = {}'.format(chr(64 + col),
                                                    row, 
                                                    cell.Formula.replace("=", ""),
                                                    cell_value))
                if highlight_formula:
                    borders = cell.Borders
                    borders.Weight = 3  # xlThick
                    borders.LineStyle = -4115  # xlDash
                    # borders.LineStyle = 1  # xlContinuous
                    borders.Color = 0xff0000  # Red color

    if highlight_formula:
        workbook.Save()
    else:
        workbook.Close(False)
    excel_app.Quit()


    if highlight_formula:
        EXE.open_file_in_default_application(excel)
        

#############
if __name__ == "__main__":
    print(__file__ + "   -----OK!")