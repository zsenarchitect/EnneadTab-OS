#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Legacy, now in view panel"
__title__ = "50_Delete view based on jpgs in folder(Legacy)"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
import time
import os
import os.path as op
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def delete_view(view):
    view_name = view.Name
    try:
        if not EA_UTILITY.is_owned(view):
            doc.Delete(view.Id)
            print("Delete view [{}]".format(view_name))
            delete_jpg_in_folder(DELETE_FOLDER, view_name)
    except Exception as e:
        if doc.ActiveView.Name == view_name:
            print("Active view cannot be deleted. Skip")
            return
        print("Cannot delete view [{}] becasue {}.".format(view_name, e))
        #t.Commit()
        #script.exit()



def delete_jpg_in_folder(output_folder, desired_name):
    EA_UTILITY.remove_exisitng_file_in_folder(output_folder, desired_name + ".jpg")


def is_no_sheet(view):
    #print view.ViewType
    if str(view.ViewType) in [ "Legend", "Schedule", "SystemBrowser", "ProjectBrowser", "DrawingSheet"]:
        return False
    if "revision" in view.Name.lower():
        return False
    if "schedule" in view.Name.lower():
        return False
    if view.IsTemplate:
        return False
    if view.LookupParameter("Sheet Number") is None:
        return True
    if view.LookupParameter("Sheet Number").AsString() == "---":
        return True
    return False


def is_view_in_folder(view):
    file_names = os.listdir(DELETE_FOLDER)

    for file_name in file_names:
        if view.Name in file_name and ".jpg" in file_name.lower():
            return True
    return False
################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:

all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()

with forms.WarningBar(title = "You can pick folder with exported jpgs"):
    DELETE_FOLDER = forms.pick_folder(title = "Pick the folder containing unwanted view jpgs")


no_sheet_views = filter(is_no_sheet, all_views)
no_sheet_views = filter(is_view_in_folder, no_sheet_views)
no_sheet_views.sort(key = lambda x:x.Name)


no_sheet_views = forms.SelectFromList.show(no_sheet_views, multiselect = True, name_attr = "Name", title = "Search the view names that you want to delete.")
if no_sheet_views is None:
    script.exit()
total = len(no_sheet_views)
counter = 0

t = DB.Transaction(doc, "delete no sheet views from folder")
t.Start()

map(delete_view, no_sheet_views)
t.Commit()


print("################### finish")
