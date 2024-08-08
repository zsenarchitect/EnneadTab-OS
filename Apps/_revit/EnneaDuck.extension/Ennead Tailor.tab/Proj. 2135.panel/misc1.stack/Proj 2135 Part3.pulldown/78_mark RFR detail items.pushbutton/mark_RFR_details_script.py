#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Mark detail items on this QAQC view with info about how many of this instance have been placed on other views of the document. And if more than one, which view.\n\nHandy after you brought in many contents from container file on day one and one day ten, you want to know how many have been deployed on the document."
__title__ = "78_Mark RFR"


from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 

# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
app = doc.Application
uidoc = __revit__.ActiveUIDocument

def get_sheet_of_view(target_view):
    all_sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).\
                ToElements()
    for sheet in all_sheets:
        view_ids = sheet.GetAllPlacedViews()
        for view_id in view_ids:
            if view_id.IntegerValue == target_view.Id.IntegerValue:
                return sheet


def mark_RFR_detail():

    # make sure current view is QAQC RFR detail display
    VIEW_KEY_NAME = "QAQC RFR DETAIL DISPLAY"

    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).\
                ToElements()
    #for x in all_views:
        #print x.Name
    my_view = filter(lambda x: VIEW_KEY_NAME in x.Name, all_views)
    if my_view is not None:
        my_view = my_view[0]
        uidoc.RequestViewChange (my_view)
        uidoc.RefreshActiveView ()




    print("-"*50)
    if  VIEW_KEY_NAME not in doc.ActiveView.Name:
        EA_UTILITY.dialogue(main_text = "Do it in view '{}' only.".format(VIEW_KEY_NAME))

        return

    print(doc.ActiveView.Name)

    all_details_placed = DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).\
                        WhereElementIsNotElementType().ToElements()
    all_details_placed = filter(lambda x: x.Category.Name == "Detail Items", all_details_placed)
    #for x in all_details_placed:
         #print x.Symbol.Family.Name
    all_details_placed = filter(lambda x: "RFR_" in x.Symbol.Family.Name, all_details_placed)

    #for x in all_details_placed:
         #print x.Symbol.Family.Name



    #get all RFR detail not placed anywhere
    all_detail_in_storage = DB.FilteredElementCollector(doc).OfClass(DB.Family).\
                            ToElements()
    #all_detail_in_storage = filter(lambda x: x.Name not in  ["System Panel",
    #"Rectangular Mullion"], all_detail_in_storage)
    all_detail_in_storage = filter(lambda x: x.FamilyCategory.Name == "Detail Items" , all_detail_in_storage)


    #all_detail_in_storage = filter(lambda x: x.Category.Name == "Detail Items", all_detail_in_storage)
    all_detail_in_storage = filter(lambda x: "RFR_" in x.Name, all_detail_in_storage)
    #print "$"*50
    #for x in all_detail_in_storage:
         #print x.Name
    #  give warning
    unique_placed_names = sorted(list(set([x.Symbol.Family.Name for x in all_details_placed])))
    unique_storaged_names = [x.Name for x in all_detail_in_storage]
    unique_storaged_names.sort()
    #print unique_placed_names
    #print unique_storaged_names
    for name in unique_storaged_names:
        if name not in unique_placed_names:
            print("<{}> not placed in anywhere, might get purged accidentally. Please place at least here.".format(name))


    # get all RFR detail instance in current view
    all_details_placed_current_view = filter(lambda x: x.OwnerViewId.IntegerValue == doc.ActiveView.Id.IntegerValue , all_details_placed)
    all_details_placed_current_view.sort(key = lambda x: x.Symbol.Family.Name)


    #get all RFR detail not in curent view
    all_details_placed_not_current_view = filter(lambda x: x.OwnerViewId.IntegerValue != doc.ActiveView.Id.IntegerValue , all_details_placed)

    unique_placed_names_in_current_view = sorted(list(set([x.Symbol.Family.Name for x in all_details_placed_current_view])))
    print("-"*50)
    for name in unique_storaged_names:
        if name not in unique_placed_names_in_current_view:
            print("<{}> not placed in QAQC view. Please place at least here.".format(name))

    unique_placed_names_not_in_current_view = sorted(list(set([x.Symbol.Family.Name for x in all_details_placed_not_current_view])))
    print("-"*50)
    for name in unique_storaged_names:
        if name not in unique_placed_names_not_in_current_view:
            print("<{}> not placed in documentation set yet. ".format(name))






    print("\n\n--------------")
    # process ite in current view, find its cousin in other view, get view location sheet number sheet etc, feed back to detail in current view.
    t = DB.Transaction(doc, "Mark RFR items in Comments")
    t.Start()
    for item in all_details_placed_current_view:
        print("\n    ")
        family_name = item.Symbol.Family.Name
        comment = ""
        for other_item in all_details_placed_not_current_view:
            if other_item.Symbol.Family.Name == family_name:
                view = doc.GetElement(other_item.OwnerViewId)
                #print "####checking " + view.Name
                detail_num_para_id = DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
                detail_num = view.Parameter[detail_num_para_id].AsString()
                #detail_num = view.LookupParameter("Detail Number"). AsString()

                sheet_num_para_id = DB.BuiltInParameter.VIEWPORT_SHEET_NUMBER
                sheet_num = view.Parameter[sheet_num_para_id].AsString()
                #sheet_num = view.LookupParameter("Sheet Number"). AsString()
                sheet = get_sheet_of_view(view)
                if sheet:
                    sheet_num = sheet.SheetNumber
                else:
                    sheet_num = "xxx"


                title_para_id = DB.BuiltInParameter.VIEW_DESCRIPTION
                view_title = view.Parameter[title_para_id].AsString()
                #view_title = view.LookupParameter("Title on Sheet"). AsString()

                #comment += "{}/{}/{}\n".format(detail_num, sheet_num,  view_title)
                comment += "{}\n".format(view.Name)
                #print "---find <{}> in {}/{}/{};".format(family_name, detail_num, sheet_num,  view_title)
                print("---find <{}> in <{}>".format(family_name, output.linkify(view.Id, title = view.Name)))
        if len(comment) == 0:
            print("---cannot find <{}> in any view".format(family_name))
            comment = "Not placed in documentation set."
        item.LookupParameter("Comments").Set(comment)


    t.Commit()

    print("\n\n--------------")
    print("tool finish")
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    mark_RFR_detail()
