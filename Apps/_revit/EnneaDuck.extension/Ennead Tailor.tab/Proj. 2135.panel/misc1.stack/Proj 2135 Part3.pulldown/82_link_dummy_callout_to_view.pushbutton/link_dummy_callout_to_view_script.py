#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Assign a stable ID when creating the dummy reference. So even if future session, the dummy callout can still find the desired view data in the link file, and update the view detail number and sheet number shown on the small circle."
__title__ = "82_Link Dummy Callout To View From Link"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument



def get_data_from_view_OLD(link_view, link_doc):
    all_sheets = DB.FilteredElementCollector(link_doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
    for sheet in all_sheets:
        for view_id in sheet.GetAllPlacedViews():
            if link_view.UniqueId == link_doc.GetElement(view_id).UniqueId:
                break

    sheet_num = sheet.SheetNumber
    if link_view.LookupParameter("Detail Number") is None:
        detail_num = "xx"
    else:
        detail_num = link_view.LookupParameter("Detail Number").AsString()

    return detail_num, sheet_num

def get_data_from_view(link_view):
    detail_num = link_view.Parameter[DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER].AsString()
    if detail_num == "" or detail_num is None:
        detail_num = "xx"

    try:
        sheet_num = link_view.Parameter[DB.BuiltInParameter.SHEET_NUMBER].AsString()
    except:
        sheet_num = "XXX"

    if sheet_num == "" or sheet_num is None or sheet_num == "XXX":
        try:
            sheet_num = link_view.LookupParameter("Sheet Number").AsString()
        except:
            sheet_num = "XXX"


    title = link_view.Parameter[DB.BuiltInParameter.VIEW_DESCRIPTION].AsString()
    if title == "":
        title = link_view.Name

    return detail_num, sheet_num, title


def is_view_on_sheet(link_view):

    """
    .ViewType.ToString() == "ViewSheet" ---> should return False as well
    """
    if link_view.LookupParameter("Sheet Number") is None:
        return False
    if link_view.LookupParameter("Sheet Number").AsString() == "---":
        return False
    return True


def link_dummy_callout_to_view():
    # get selection and check if is bili linker
    selection_ids = uidoc.Selection.GetElementIds ()
    selection = [doc.GetElement(x) for x in selection_ids]
    if len(selection) != 1:
        EA_UTILITY.dialogue(main_text = "Pick one <Bili Cross Doc Callout> item only.")
        return

    dummy = selection[0]
    if dummy.Symbol.FamilyName != "Bili_Cross Doc_Callout Dummy" :
        EA_UTILITY.dialogue(main_text = "Pick one <Bili Cross Doc Callout> item only.")
        return


    # pick from linked doc

    link_doc = EA_UTILITY.select_revit_link_docs(select_multiple = False)

    # get view from link doc and select from list
    all_link_views = DB.FilteredElementCollector(link_doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()


    all_link_views = filter(is_view_on_sheet, all_link_views)

    class MyOption(forms.TemplateListItem):


        @property
        def name(self):
            #detail_num, sheet_num = get_data_from_view(self.item, link_doc)

            detail_num, sheet_num, title = get_data_from_view(self.item)
            return "[{}/{}]{}".format( sheet_num, detail_num, title)
            #return "{}".format( self.item.Name)#

    ops = [MyOption(x) for x in all_link_views]
    ops.sort(key = lambda x: x.name)
    link_view = forms.SelectFromList.show(ops, multiselect = False, title = "Pick a view to set a link into.")




    # get detail number, sheet number, plot ID and assign to family
    view_stable_id = link_view.UniqueId
    plot_id = link_doc.Title.replace("2135_BiliBili SH HQ_", "")


    detail_num, sheet_num, title = get_data_from_view(link_view)
    """
    print(link_view.LookupParameter("Detail Number").AsString())
    print(link_view.Parameter[DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER].AsString())
    print(link_view.Parameter[DB.BuiltInParameter.VIEWER_DETAIL_NUMBER].AsString())

    print("#"*5)
    print(link_view.LookupParameter("Sheet Number").AsString())
    print(link_view.Parameter[DB.BuiltInParameter.SHEET_NUMBER].AsString())
    """



    """
    if link_view.LookupParameter("Sheet Number") is None:
        sheet_num = "xxx"
    else:
        sheet_num = link_view.LookupParameter("Sheet Number").AsString()
    """

    #print detail_num, sheet_num
    #detail_num, sheet_num = get_data_from_view(link_view, link_doc)
    t = DB.Transaction(doc, "Link into link doc view for this dummy")
    t.Start()
    dummy.LookupParameter("data_source view stableId").Set(view_stable_id)
    dummy.LookupParameter("data_source plot Id").Set(plot_id)
    dummy.LookupParameter("detail number").Set(detail_num)
    dummy.LookupParameter("sheet num").Set(sheet_num)
    dummy.LookupParameter("view full name").Set(link_view.Name)
    dummy.LookupParameter("view title").Set(title)

    t.Commit()

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    link_dummy_callout_to_view()
