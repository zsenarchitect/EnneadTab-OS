
#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Locate sections in the viewport of the sheet that is refering to views from other sheet. For system drawing, most detail section mark should refer to current sheet."
__title__ = "81_find_section_mark_not_from_sheet"

from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def is_on_current_sheet(view, sheet_num):
    all_sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
    sheet = filter(lambda x: x.SheetNumber == sheet_num, all_sheets)[0]
    for view_id in sheet.GetAllPlacedViews():
        if doc.GetElement(view_id).Name == view.Name:
            return True
    return False

def get_source_view_scale(ref_view):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    source_view = filter(lambda x: x.Name == ref_view.Name, all_views)[0]
    return source_view.Scale

def process_view(view_id, sheet_num):

    view = doc.GetElement(view_id)
    print("\n\n Checking <{}>---------".format(output.linkify(view.Id, title = view.Name)))
    #section_marks = DB.FilteredElementCollector(doc, view_id).OfCategory(DB.BuiltInCategory.OST_Sections).ToElements()
    #section_marks = DB.FilteredElementCollector(doc, view_id).OfCategory(DB.BuiltInCategory.OST_Views).ToElements()
    #section_marks = DB.FilteredElementCollector(doc, view_id).OfClass(DB.ViewSection).ToElements()
    #if len(section_marks) != 0:
    #print section_marks
    everything = DB.FilteredElementCollector(doc, view_id).ToElements()
    #unique_cate = sorted(list(set([x.Category.Name for x in everything if x.Category is not None])))
    #print unique_cate
    for item in everything:
        if item.Category is None:
            continue
        if item.Category.Name == "Views":
            print("  Find view marker <{}>".format(item.Name))
            #print item
            #print item.GetType()
            #actual_view = doc.GetElement(DB.ReferenceableViewUtils.GetReferencedViewId (doc, item.Id))
            #print actual_view.ViewType
            #for para in item.Parameters():
                #print para.Definition.Name
            if not is_on_current_sheet(item, sheet_num):
                print("    <{}> is not refering to a viewport on this sheet.".format(output.linkify(item.Id, title = item.Name)))
                scale = get_source_view_scale(item)
                if scale > 20:
                    print("$"*50)
                    output.print_md( "***Above Refering view scale is*** [{}], larger than 20, **potentially is a system view not a detail view.** ".format(scale))
                    print("$"*50)
                    print("\n\n  ")
    #section_marks = DB.FilteredElementCollector(doc, view_id).OfCategory(DB.BuiltInCategory.OST_Views).ToElements()
    #print section_marks

def find_section_mark_not_from_sheet():
    sheets = forms.select_sheets()
    if not sheets:
        return
    for sheet in sheets:
        print("\n\n ###############################Checking sheet <{}>####################".format(output.linkify(sheet.Id, title = sheet.SheetNumber)))
        sheet_num = sheet.SheetNumber
        map(lambda x:process_view(x, sheet_num), sheet.GetAllPlacedViews())
    pass

    print("-"*100)
    print("TOOL FINISH")
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    find_section_mark_not_from_sheet()
