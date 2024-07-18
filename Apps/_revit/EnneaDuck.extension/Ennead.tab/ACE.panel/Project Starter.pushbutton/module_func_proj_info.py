
from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import forms

from EnneadTab import NOTIFICATION, ERROR_HANDLE
import os

@ERROR_HANDLE.try_catch_error()
def set_proj_info(doc, data):

    t = DB.Transaction(doc, "Set Project Info")
    t.Start()
    
    for key, value in data.items():
        if value == "":
            continue
        if key == "FileName":
            continue
        setattr(doc.ProjectInformation, key, value)
    t.Commit()
    
    if data["FileName"] != "":
        # folder = forms.pick_folder(title = "Where the file is saved?")
        path = forms.save_file(file_ext="rvt", 
                               default_name=data["FileName"],
                               title = "Where the file is saved?")
        if not path:
            NOTIFICATION.messenger (main_text =  "No filepath set.")
        else:
            if os.path.exists(path):
                NOTIFICATION.messenger (main_text =  "There is a same name file in the location. Will cancel saving.")
            else:
                option = DB.SaveAsOptions ()
                if not doc.IsWorkshared:
                    doc.EnableWorksharing ('0_Shared Levels & Grids', "Everything Else")
                workshare_options = DB.WorksharingSaveAsOptions ()
                workshare_options.SaveAsCentral = True
                option.SetWorksharingOptions (workshare_options)
                # optoin.OpenWorksetsDefault # this control how trh default workset behavou during opening is , default to USER Spec
                doc.SaveAs(path, option)
                # doc.SaveAs("{}\{}.rvt".format(folder, data["FileName"]))

    NOTIFICATION.messenger (main_text =  "Project Parameter Set")

if __name__== "__main__":
    pass