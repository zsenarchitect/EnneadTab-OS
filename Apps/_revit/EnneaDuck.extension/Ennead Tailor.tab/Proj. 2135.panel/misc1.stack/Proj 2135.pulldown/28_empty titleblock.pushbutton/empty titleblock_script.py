#!/usr/bin/python
# -*- coding: utf-8 -*-
__title__ = "28_Set/Reset Empty Titleblock."
__doc__ = "Some LDI prefer a totally empty titleblock. Unfortunately, the revision schedule cannot be turned on/off by parameter control. SO this tool, will remove the sheet revisions, and store that information at the issue parameters. Then the titleblock can be turned empty. After the export, the tool can be used to recover sheet revision schedule.\n\nWhy not switch to another empty titleblock family? Becasue when switching, non-shared-instance-parameter will reset.So you will lose any local setting."
from pyrevit import forms, script #
from Autodesk.Revit import DB # pyright: ignore 
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
# uidoc = __revit__.ActiveUIDocument
# app = doc.Application

import EA_UTILITY
import EnneadTab

# from Autodesk.Revit import UI # pyright: ignore
# uiapp = UI.UIApplicationapp
# uidoc = UI.UIDocument
# #optional
# host_app = pyrevit._HostApplication
# app = host_app.app
# uiapp = host_app.uiapp
# uidoc = host_app.uidoc




"""
from pyrevit import HOST_APP
doc = HOST_APP.doc
uidoc = HOST_APP.uidoc
"""



def update_titleblock():
    titleblock_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()

    for titleblock_type in titleblock_types:
        if titleblock_type.Family.Name not in ["TTBLK_A0_Vert", "TTBLK_A1_Vert"]:
            continue
        print("fixing titleblock [{}]".format(titleblock_type.Family.Name))
        titleblock_type.LookupParameter("#use empty titleblock").Set(not will_restore)

def get_revision_by_para(para_name):

    index = para_names.index(para_name)
    revision_name = revision_names[index]

    revisions = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Revisions).WhereElementIsNotElementType().ToElements()

    return filter(lambda x: revision_name == x.Description, revisions)[0]


def set_revision_on_sheet(sheet):

    new_revision_list = []
    for para_name in para_names:
        try:
            is_issue = sheet.LookupParameter(para_name).AsString()
            if len(is_issue) == 0:
                pass
            else:

                new_revision_list.append(get_revision_by_para(para_name))
        except Exception as e:
            #this para is not here, dont worry about it.
            pass
    collection = EA_UTILITY.list_to_system_list([x.Id for x in new_revision_list])
    sheet.SetAdditionalRevisionIds(collection)


def process_sheet(sheet):
    print("working on sheet [{}]".format(sheet.Name))
    if will_restore:
        set_revision_on_sheet(sheet)
    else:
        sheet.SetAdditionalRevisionIds(EA_UTILITY.list_to_system_list([]))


################## main code below #####################
output = script.get_output()
output.close_others()

options = ["make empty", "restore"]
# ask to make empty or reset titbleblock
res = forms.alert("I want to [...] titleblock", options = options)
if res == options[0]:
    will_restore = False
elif res == options[1]:
    will_restore = True
else:
    script.exit()


# gat all sheets
all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

filepath = r"I:\2135\0_BIM\10_BIM Management\Revision and Para List.txt"
raw_data = EA_UTILITY.read_txt_as_list(filepath, use_encode = True)
revision_names = [x.split("-----")[0] for x in raw_data]
para_names = [x.split("-----")[1] for x in raw_data]




# map process
t = DB.Transaction(doc, "{} titleblock".format(res))
t.Start()
map(process_sheet, all_sheets)
print("---")
update_titleblock()
t.Commit()
