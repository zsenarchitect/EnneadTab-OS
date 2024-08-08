#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Transfer the data between issing parameter and titleblock revision schedule. Also can transfer issue data from last round to current round."
__title__ = "18_set bullit point by/to revision on sheet"

from pyrevit import forms, DB, revit, script
import System
import EA_UTILITY
import EnneadTab

def get_para_by_revision(revision):
    """
    global revision_names
    global para_names
    """
    #print revision.Name.split(" - ")[1]
    index = revision_names.index(revision.Name.split(" - ")[1])

    return para_names[index]

def get_revision_by_para(para_name):
    """
    global revision_names
    global para_names
    """
    #print revision.Name.split(" - ")[1]
    if para_name == r"Issue 2022/09/29":
        para_name = r"Issue 2022/09/30"
    #index = para_names.index(para_name)
    #print index
    #revision_name = revision_names[index]
    #print revision_name
    revisions = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Revisions).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: para_name.replace("Issue ", "") == x.RevisionDate, revisions)[0]
    return filter(lambda x: revision_name == x.Description, revisions)[0]

def reset_para_on_sheet(sheet):
    revisions = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Revisions).WhereElementIsNotElementType().ToElements()
    for revision in revisions:
        sheet.LookupParameter(get_para_by_revision(revision)).Set("")


#def update_issues_blackSQ_on_sheet(sheet, revisions):
def update_issues_blackSQ_on_sheet(sheet):
    reset_para_on_sheet(sheet)
    revisions_on_sheet = [revit.doc.GetElement(x) for x in sheet.GetAllRevisionIds()]
    for revision in revisions_on_sheet:
        #unicode_string = u"\u25A0".encode('utf-8')
        unicode_string = u"\u25A0"
        sheet.LookupParameter(get_para_by_revision(revision)).Set(unicode_string)
        #print get_para_by_revision(revision)

def set_revision_on_sheet(sheet):
    """
    global revision_names
    global para_names
    """
    print sheet.SheetNumber
    new_revision_list = []
    for para_name in para_names:
        try:
            para = sheet.LookupParameter(para_name)
            if para is None:
                continue
            is_issue = sheet.LookupParameter(para_name).AsString()
            #print is_issue
            if len(is_issue) == 0:
                #print "*"*60
                #remove revision from sheet
                pass
            else:
                #add revision on sheet
                #print "append {} to to-do list".format(para_name)
                new_revision_list.append(get_revision_by_para(para_name))
        except Exception as e:
            #print (e)
            #this para is not here, dont worry about it.
            pass
    #print new_revision_list
    collection = System.Collections.Generic.List[DB.ElementId]([x.Id for x in new_revision_list])
    #print collection
    sheet.SetAdditionalRevisionIds(collection)
    pass


def create_printset():
    para_name = forms.alert("use which issue status to create print set?", options = para_names[-4:])
    temp_set = DB.ViewSet()


    matching_sheets = []
    for sheet in sheets:
        #print sheet.SheetNumber
        try:
            if len(sheet.LookupParameter(para_name).AsString()) != 0:
                matching_sheets.append(sheet)
        except:
            pass

    #matching_sheets = filter(lambda x: x.LookupParameter(para_name).HasValue, list(sheets))
    map(lambda x: temp_set.Insert(x), matching_sheets )
    print_manager = revit.doc.PrintManager
    print_manager.PrintRange = DB.PrintRange.Select
    setting = print_manager.ViewSheetSetting
    setting.CurrentViewSheetSet.Views = temp_set
    while True:
        try:
            name = forms.ask_for_string("PrintSet Name to save to file...", title = "name for PrintSet")
            setting.SaveAs(name)
            break
        except:
            forms.alert("This name is already in use.")


def set_square_manually():
    #sheets = forms.select_sheets()
    sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    unicode_string = u"\u25A0"

    key_para_from_before = forms.ask_for_one_item(para_names, default = para_names[-2], prompt = "pick an old issue to extract usage from", title = None)
    key_para_to_assign = forms.ask_for_one_item(para_names, default = para_names[-1], prompt = "pick a new issue to transfer usage into", title = None)

    for sheet in sheets:
        if sheet.LookupParameter(key_para_from_before).AsString() == unicode_string:
            sheet.LookupParameter(key_para_to_assign).Set(unicode_string)
################## main code below #####################
output = script.get_output()
output.close_others()

#revisions = forms.select_revisions(button_name='Select Revision',multiple=True)
#revisions = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Revisions).WhereElementIsNotElementType().ToElements()

"""
revision_names = ["政府征询70%阶段性成果 Gov. Set 70%",\
                    "政府征询85%阶段性成果 Gov. Set 85%",\
                    "政府征询100%阶段性成果 Gov. Set 100%",\
                    "50% SD Set"]

para_names = [r"Issue 2021/12/31",\
                r"Issue 2022/01/15",\
                r"Issue 2022/02/25",\
                r"Issue 2022/03/10"]
"""

filepath = r"I:\2135\0_BIM\10_BIM Management\Revision and Para List.txt"
raw_data = EA_UTILITY.read_txt_as_list(filepath, use_encode = True)
revision_names = [x.split("-----")[0] for x in raw_data]
para_names = [x.split("-----")[1] for x in raw_data]

sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()


workflow_options = ["revision on sheet--->black square status on schedule", "black square status on schedule--->revision on sheet", "create PrintSet by black square status","transfer [issue] black square from older issue"]
res = forms.alert("workflow", options = workflow_options)


with revit.Transaction(res):
    #map(lambda x: update_issues_blackSQ_on_sheet(x, revisions), sheets)
    if res == workflow_options[0]:
        map(update_issues_blackSQ_on_sheet, sheets)

    elif res == workflow_options[1]:
        map(set_revision_on_sheet, sheets)

    elif res == workflow_options[2]:
        create_printset()

    elif res == workflow_options[3]:
        set_square_manually()
    else:
        pass


print "Tool Finished"
