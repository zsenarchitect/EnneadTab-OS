#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Export the filled region color setting to excel so you can use it elsewhere."
__title__ = "Export Filled\nRegion Types"
__tip__ = True

# from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, FOLDER, EXCEL, LOG
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


from EXCEL import ExcelDataItem # pyright: ignore 

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def export_filled_region_types():
    
    solid_pattern_id = REVIT_SELECTION.get_solid_fill_pattern_id()
    all_filled_region_types = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).ToElements()
    all_filled_region_types = sorted(all_filled_region_types, key = lambda x: x.LookupParameter("Type Name").AsString())

    data = []
    for i, filled_region_type in enumerate(all_filled_region_types):
        row = i + 1
        masker_color = (255,255, 255) if filled_region_type.IsMasking else (200, 200, 200)
        type_name = filled_region_type.LookupParameter("Type Name").AsString()
        data.append(ExcelDataItem(type_name, row, "A", masker_color))

        is_mask = "Yes" if filled_region_type.IsMasking else "No"
        data.append(ExcelDataItem(is_mask, row, "B", masker_color))

        # foregrtound
        foreground_color = filled_region_type.ForegroundPatternColor
        if solid_pattern_id == filled_region_type.ForegroundPatternId:
            foreground_pattern = "Solid"
        else:
            pattern = doc.GetElement(filled_region_type.ForegroundPatternId)
            if pattern:
                foreground_pattern = pattern.Name
            else:
                foreground_pattern = None
                
        color_pack = (foreground_color.Red,
                    foreground_color.Green,
                    foreground_color.Blue)
        color_text = "{}-{}-{}".format(*color_pack)
        data.append(ExcelDataItem(color_text, row, "D"))
        if not foreground_pattern:
            data.append(ExcelDataItem("Void", row, "C", text_color = color_pack))
            data.append(ExcelDataItem("Void", row, "E"))
        else:
            data.append(ExcelDataItem("", row, "C", cell_color = color_pack))
            data.append(ExcelDataItem(foreground_pattern, row, "E"))


        #background
        background_color = filled_region_type.BackgroundPatternColor
        if solid_pattern_id == filled_region_type.BackgroundPatternId:
            background_pattern = "Solid"
        else:
            pattern = doc.GetElement(filled_region_type.BackgroundPatternId)
            if pattern:
                background_pattern = pattern.Name
            else:
                background_pattern = None
  
        color_pack = (background_color.Red,
                    background_color.Green,
                    background_color.Blue)
        # print (color_pack)
        color_text = "{}-{}-{}".format(*color_pack)
        data.append(ExcelDataItem(color_text, i+1, 'G'))
        if not background_pattern:
            data.append(ExcelDataItem("Void", i+1, "F", text_color = color_pack))
            data.append(ExcelDataItem(background_pattern, i+1, 'H'))
        else:
            data.append(ExcelDataItem("", i+1, "F", cell_color = color_pack))
            data.append(ExcelDataItem(background_pattern, i+1, 'H'))



    
    data.append(ExcelDataItem("FilledRegionType", 0, 'A'))
    data.append(ExcelDataItem("IsMasking", 0, 'B'))
    data.append(ExcelDataItem("ForegroundColor", 0, 'C'))
    data.append(ExcelDataItem("ForegroundColorRGB", 0, 'D'))
    data.append(ExcelDataItem("ForegroundPattern", 0, 'E'))
    data.append(ExcelDataItem("BackgroundColor", 0, 'F'))
    data.append(ExcelDataItem("BackgroundColorRGB", 0, 'G'))
    data.append(ExcelDataItem("BackgroundPattern", 0, 'H'))

    filepath = FOLDER.get_EA_dump_folder_file("FilledRegionColor.xlsx")
    EXCEL.save_data_to_excel(data, filepath, worksheet = "EnneadTab", open_after = True)




################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    export_filled_region_types()
    







