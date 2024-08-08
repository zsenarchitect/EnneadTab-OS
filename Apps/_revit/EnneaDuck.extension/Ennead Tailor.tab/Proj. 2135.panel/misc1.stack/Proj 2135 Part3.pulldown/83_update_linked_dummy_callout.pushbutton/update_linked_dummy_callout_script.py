#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Update the view detail number and sheet number data based on the linked dummy callout. You need to have the related link loaded for it to find the linked view."
__title__ = "83_Update Linked Dummy Callout"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore



def process_dummy(dummy):
    #print dummy
    # get plot id, stable view id
    view_stable_id = dummy.LookupParameter("data_source view stableId").AsString()
    if view_stable_id == "":
        return

    plot_id = dummy.LookupParameter("data_source plot Id").AsString()

    # get link doc, if not loaded give warning
    docs = doc.Application.Documents
    for link_doc in docs:
        if "_{}".format(plot_id) in link_doc.Title:
            break
    else:
        print("Cannot find doc " + plot_id + " in the loaded links.")
        return


    # get the view by stable id,
    link_view = link_doc.GetElement(view_stable_id)
    if not link_view:
        print("Cannot find view by the stable Id")
        return

    detail_num = dummy.LookupParameter("detail number").AsString()
    sheet_num = dummy.LookupParameter("sheet num").AsString()
    title = dummy.LookupParameter("view title").AsString()
    record = "{}/{}/{}".format(sheet_num, detail_num, title)


    # get tile, view name, sheet number, detail number
    detail_num, sheet_num, title = get_data_from_view(link_view)
    dummy.LookupParameter("detail number").Set(detail_num)
    dummy.LookupParameter("sheet num").Set(sheet_num)
    dummy.LookupParameter("view full name").Set(link_view.Name)
    dummy.LookupParameter("view title").Set(title)

    #owner_view = doc.GetElement(dummy.OwnerViewId )
    #print owner_view
    print("\n------------------")
    print("Getting update to dummy callout {}.".format(output.linkify(dummy.Id, title = "Click to show Dummy Callout")))
    print("{}-->{}/{}/{}".format(record, sheet_num, detail_num, title))


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


def update_linked_dummy_callout():
    # get all family instance of dummy
    all_instances = DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WhereElementIsNotElementType().ToElements()

    dummies = filter(lambda x: x.Symbol.FamilyName == "Bili_Cross Doc_Callout Dummy", all_instances)

    # process each
    t = DB.Transaction(doc, "Link into link doc view for this dummy")
    t.Start()
    map(process_dummy, dummies)
    t.Commit()
    pass
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    update_linked_dummy_callout()
