#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Use me tp export selected Color Scheme To Excel. You have the option to exclude unused color."
__title__ = "ColorScheme\nTo Excel"
__tip__ = True
from pyrevit import forms #
from pyrevit import script #
import xlsxwriter as xw

import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS
from EnneadTab import ERROR_HANDLE, NOTIFICATION, COLOR, EXE, DATA_FILE
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
            
@ERROR_HANDLE.try_catch_error()
def export_color_scheme():
    
    color_schemes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ColorFillSchema).WhereElementIsNotElementType().ToElements()
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            cate_name = DB.Category.GetCategory(doc, self.item.CategoryId).Name
            return "[{}]: {}".format(cate_name, self.item.Name)

    options = [MyOption(x) for x in color_schemes]
    color_schemes = forms.SelectFromList.show(context = sorted(options, key = lambda x: x.name),
                                        title = "Pick the color scheme to export the data.",
                                        multiselect = True)

    if not color_schemes:
        return
    
    opts = ["Yes, only show me used color", "No, show me every color"]
    res = REVIT_FORMS.dialogue(main_text = "Should it ignore the color that is not in use?", options = opts)
    is_ignore_non_used = True if res == opts[0] else False
    # for entry in color_scheme.GetEntries():
        
    #     print entry.GetStringValue ()
    #     print entry.Color.Red, entry.Color.Green, entry.Color.Blue
    #     print entry.IsInUse
        
        
        
    for color_scheme in color_schemes:
        export_color_scheme_to_excel(color_scheme, is_ignore_non_used)
    # Create a workbook and add a worksheet.
    #forms.save_excel_file()

def export_color_scheme_to_excel(color_scheme, is_ignore_non_used):
    cate_name = DB.Category.GetCategory(doc, color_scheme.CategoryId).Name
    excel_name =  "[{}] {}".format(cate_name, color_scheme.Name)
    file_location = forms.save_file(file_ext='xlsx',
                                    default_name=excel_name)
    workbook = xw.Workbook(file_location)
    worksheet = workbook.add_worksheet("Color Scheme")

    hex_color = COLOR.rgb_to_hex((120,120,120))
    format = workbook.add_format({'bg_color' : hex_color})
    worksheet.write(0,0,"Parameter Value", format)
    worksheet.set_column(0,0, 35)
    worksheet.write(0,1,"Is In Use", format)
    worksheet.write(0,2,"Color", format)
    worksheet.write(0,3,"Color R", format)
    worksheet.write(0,4,"Color G", format)
    worksheet.write(0,5,"Color B", format)
    
    if is_ignore_non_used:
        entries = [entry for entry in color_scheme.GetEntries() if entry.IsInUse]
    else:
        entries = color_scheme.GetEntries()
        
    
    alt_dict = {}
    
    
    for i, entry in enumerate(entries):
        i += 1
        if not entry.Color.IsValid:
            print ("Color is not valid for <{}>".format(entry.GetStringValue ()))
            continue
        alt_dict[entry.GetStringValue ()] = [int(entry.Color.Red),
                                            int(entry.Color.Green),
                                            int(entry.Color.Blue)]
        
        
        worksheet.write(i,0,entry.GetStringValue ())
        worksheet.write(i,1,"Yes" if entry.IsInUse else "No")
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(entry.Color.Red),
                                                 int(entry.Color.Green),
                                                 int(entry.Color.Blue))
                                                 
        format = workbook.add_format({'bg_color' : hex_color})
        worksheet.write(i, 2, " ", format)
        worksheet.write(i,3,entry.Color.Red)
        worksheet.write(i,4,entry.Color.Green)
        worksheet.write(i,5,entry.Color.Blue)
        
        
    DATA_FILE.set_data(alt_dict, "color_scheme_dict.sexyDuck")

    
    
    try:
        workbook.close()
        NOTIFICATION.messenger("Excel saved at '{}'".format(file_location))
        EXE.try_open_app(file_location)
    except:
        NOTIFICATION.messenger("the excel file you picked is still open, cannot override. Writing cancelled.")
    


    
    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
"""
def try_catch_error(func):
    def wrapper(*args, **kwargs):
        print("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            return func(*args, **kwargs)
        except Exception as e:
            print(str(e))
            return "Wrapper func for EA Log -- Error: " + str(e)
    return wrapper
"""
"""
    phase_provider = DB.ParameterValueProvider( DB.ElementId(DB.BuiltInParameter.ROOM_PHASE))
    phase_rule = DB.FilterElementIdRule(phase_provider, DB.FilterNumericEquals(), phase.Id)
    phase_filter = DB.ElementParameterFilter(phase_rule)
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WherePasses(phase_filter).WhereElementIsNotElementType().ToElements()
    return all_rooms
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    export_color_scheme()
    



