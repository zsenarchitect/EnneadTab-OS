#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Find doors from this project that are not tagged yet. You can pick sheets to process. Only plan views will be considered.\n\nRequested by J.H.Park"
__title__ = "Find All Door Not Tagged"

from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
            
BAD_NAMES = ["B - DR-Opening",
            "B - DR-Opening-Framed",
            "Detail-Door Swing",
            "Detail-Door Swing-Hidden", 
            "Detail-Door Swing-Slider"]


@EnneadTab.ERROR_HANDLE.try_catch_error
def find_all_door_tag():
    
    sheets = forms.select_sheets(title = "Select sheets to find door tags")
    if not sheets:
        return
    
    for sheet in sheets:
        print ("\n\n Checking sheet:<{}-{}>".format(sheet.SheetNumber, sheet.Name))
        for view_id in sheet.GetAllPlacedViews ():
            view = doc.GetElement(view_id)
            print ("---+ Checking view:<{}>".format(output.linkify(view_id, title = view.Name)))
            
            if view.ViewType != DB.ViewType.FloorPlan:
                continue
            
            all_door_ids = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElementIds()
            # print all_doors[0].LevelId.IntegerValue
            # print view.GenLevel .Id.IntegerValue 
            # all_door_ids = [door.Id for door in all_doors if door.LevelId.IntegerValue == view.GenLevel.Id.IntegerValue ]
            
            all_door_tags = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_DoorTags).WhereElementIsNotElementType().ToElements()
            # print all_doors
            # print all_door_tags
            tagged_door_ids_local = set()
            tagged_door_ids_all = set()
            for door_tag in all_door_tags:
                for door_id in door_tag.GetTaggedLocalElementIds():

                    tagged_door_ids_local.add(door_id)
                    
                for door_id in door_tag.GetTaggedElementIds ():
                    tagged_door_ids_all.add(door_id)
                    
            untagged_door_ids_local = set(all_door_ids) - tagged_door_ids_local
            for door_id in untagged_door_ids_local:
                if is_excluded_family(door_id):
                    continue
                print ("---| Door <{}> is not tagged".format(output.linkify(door_id)))
            
            if not EnneadTab.USER.is_SZ():
                continue
            continue
             
            
            # everythign is cast as LinkElementId, but only true link element has valid Id with "LinkedElementId" property, so can use this to filter out the link from local.-------note for future me.
            door_ids_link = tagged_door_ids_all - tagged_door_ids_local
            print(tagged_door_ids_all)
            print(tagged_door_ids_local)
            print(door_ids_link)
            for door_id in door_ids_link:
                print(door_id)
                print(door_id.LinkInstanceId)
                print(door_id.LinkedElementId)
            if len(door_ids_link) == 0:
                continue
            for door_id in door_ids_link:
                print ("Find a door from a revit link")
                continue
                # if is_excluded_family(door_id):
                #     continue
                print ("!!!Door <{}> is from a revit link.".format(output.linkify(door_id)))
            

    print ("\n\n-------------------Done!-------------------")
    print ("Below families are excluded in the search:")
    for name in BAD_NAMES:
        print ("<" + name + ">")
        
        
def is_excluded_family(door_id):
    try:
        door = doc.GetElement(door_id)
    except:
        print(door_id)
        print(door_id.LinkInstanceId)
        print(door_id.LinkedElementId)
        link_doc = doc.GetElement(door_id.LinkInstanceId)
        door = link_doc.GetElement(door_id.LinkedElementId)
    if door.Symbol.Family.Name in BAD_NAMES:
        return True
    return False    

  
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    find_all_door_tag()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)



