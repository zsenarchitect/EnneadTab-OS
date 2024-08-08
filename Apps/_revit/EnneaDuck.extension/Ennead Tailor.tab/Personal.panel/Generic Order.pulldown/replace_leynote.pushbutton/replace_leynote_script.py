#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Find and replace user keynote with annotation symbol."
__title__ = "Replace Keynote With Symbol"

from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def get_type(family_name, type_name):
    all_symbol_types = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol ).WhereElementIsElementType().ToElements()
    for symbol_type in all_symbol_types:
         
       if symbol_type.Family.Name == family_name and symbol_type.LookupParameter("Type Name").AsString() == type_name:
           return symbol_type
    return None
 
@EnneadTab.ERROR_HANDLE.try_catch_error()
def replace_leynote():
    

    user_keynote_search = forms.ask_for_string(prompt="The content of user keynote to search for.\nUse empty for search/replace all.")
    
    #symbol = get_type("SYMBOL_Centerline", "Standard")
    family = EnneadTab.REVIT.REVIT_SELECTION.pick_family(doc)
    if not family:
        return
    symbol_types = EnneadTab.REVIT.REVIT_SELECTION.pick_type(family)
    if not symbol_types:
        print("Cannot find this type")
        
        return
    
    
    keynote_tags = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_KeynoteTags).WhereElementIsNotElementType().ToElements()
    user_tags = [tag for tag in keynote_tags if tag.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString() == "User" ]
    
    
    t = DB.Transaction(doc, __title__)
    t.Start()

    for tag in user_tags:
        
        if user_keynote_search != "" and tag.TagText != user_keynote_search:
            continue
        
        
        print("\n\n   ")
        print("*"*20)
        print(output.linkify(tag.Id, title = "go to tag" ))
        if hasattr(tag, "TagText") and tag.TagText != "":
            print("Display Content = {}".format(tag.TagText))
            
        head_position = tag.TagHeadPosition 
        # HasLeader
        ref = tag.GetTaggedReferences ()[0]
        if tag.HasLeader:
            leader_end_position = tag.GetLeaderEnd (ref)
        else:
            leader_end_position = None
        if tag.HasLeader and tag.HasLeaderElbow (ref):
            elbow_position = tag.GetLeaderElbow (ref)
        else:
            elbow_position = None
        # SetLeaderElbow ()
        # SetLeaderEnd ()

        
        new_symbol = doc.Create.NewFamilyInstance (head_position, symbol_types, doc.GetElement(tag.OwnerViewId))
        if not tag.HasLeader:
            continue
        new_symbol.addLeader()
        leader = new_symbol.GetLeaders()[0]
        if elbow_position:
            leader.Elbow = elbow_position
        if leader_end_position:
            leader.End = leader_end_position

    t.Commit()
    
    print ("\n\n\n\n  ")
    print ("#"*20)
    print ("Finished!!")
    
    
"""
def try_catch_error(func):
    def wrapper(*args, **kwargs):
        print("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            return func(*args, **kwargs)
        except Exception as e:
            print(str(e))
            return "Wrapper func for EA Log -- Error: " + str(e)
    return wrapper
"""
"""
    phase_provider = DB.ParameterValueProvider( DB.ElementId(DB.BuiltInParameter.ROOM_PHASE))
    phase_rule = DB.FilterElementIdRule(phase_provider, DB.FilterNumericEquals(), phase.Id)
    phase_filter = DB.ElementParameterFilter(phase_rule)
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WherePasses(phase_filter).WhereElementIsNotElementType().ToElements()
    return all_rooms
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    replace_leynote()
    











