#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """
This shows the history of warnings for file(s) that had been recorded by EnneadTab

Left Click: Check current document.
Shift Click: Check results from a selection of projects. 
"""
__title__ = "Display Revit\nWarning History"
__tip__ = True
import os
from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION, REVIT_HISTORY
from EnneadTab import ENVIRONMENT, OUTPUT, NOTIFICATION, ERROR_HANDLE
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
            
@ERROR_HANDLE.try_catch_error()
def display_warning_history(using_current = True):

    if using_current and doc.IsFamilyDocument:
        NOTIFICATION.messenger(main_text="You cannot check current history on a family document.\nBut you can check others. Try Shift Click this button again.")
        
        return

    show_detail = True
    opts= ["Yes, show details", "No details, just graph"]
    res = REVIT_FORMS.dialogue(main_text="Would you like to see the details of the warnings?",options = opts)
    if not res:
        return
    if res == opts[1]:
        show_detail = False
    
    if using_current:
        hint_chart_js()
        REVIT_HISTORY.display_warning(doc.Title, show_detail=show_detail)
        return
    
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return self.item.replace("REVIT_WARNING_HISTORY_", "").replace(".sexyDuck", "")
    folder = ENVIRONMENT.DUMP_FOLDER or ENVIRONMENT.SHARED_DATA_DUMP_FOLDER

    file_list = [MyOption(x) for x in os.listdir(folder) if x.startswith("REVIT_WARNING_HISTORY_")]
    file_list.sort(key=lambda x: x.name)
    res = forms.SelectFromList.show(file_list,
                                     button_name = "Select Document(s)",
                                     multiselect = True,
                                     title = "Ok, wehre to dig the deets.")
    if not res:
        return

    hint_chart_js()
    for item in res:
        REVIT_HISTORY.display_warning(item.replace("REVIT_WARNING_HISTORY_", "").replace(".sexyDuck", ""),
                                                      show_detail=show_detail)
    
    # OUTPUT.display_output_on_browser()
    print("Done")

def hint_chart_js():
    hint_image = script.get_bundle_file("chart js hint.png")

    NOTIFICATION.messenger(main_text="When asked about loading java script, click 'yes'",
                                     image = hint_image)
################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    if __shiftclick__:
        display_warning_history(using_current=False)
    else:
        display_warning_history()
    


