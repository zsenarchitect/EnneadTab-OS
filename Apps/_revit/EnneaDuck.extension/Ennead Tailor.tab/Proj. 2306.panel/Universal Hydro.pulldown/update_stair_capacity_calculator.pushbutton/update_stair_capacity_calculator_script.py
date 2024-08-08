#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Gather the room life safety data from rooms of each level can sum and feed into the Stair Capacity Calculator for capacity required."
__title__ = "(Depreciated)Update Stair Capacity Calculator"

import math
# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
try:
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
except:
    pass

def get_room_final_capacity(room, show_log = True):
    if not room.LookupParameter("Rooms_Occupancy Manual").HasValue and EnneadTab.REVIT.REVIT_SELECTION.is_changable(room):
        room.LookupParameter("Rooms_Occupancy Manual").Set(-1)
        
    # ignore rooms whose AreaPerPerson is negative
    if room.LookupParameter("Rooms_Occupancy AreaPerPerson").AsDouble() < 0:
        return 0
    
    # pioritise manual override
    if room.LookupParameter("Rooms_Occupancy Manual").AsInteger() >= 0:
        return room.LookupParameter("Rooms_Occupancy Manual").AsInteger()
    
    # print room.LookupParameter("Rooms_Occupancy AreaPerPerson").AsDouble ()
    
    if room.LookupParameter("Rooms_Occupancy AreaPerPerson").AsDouble () == 0 or not room.LookupParameter("Rooms_Occupancy AreaPerPerson").HasValue:
        if show_log:
            print ("No Rooms_Occupancy AreaPerPerson for {}. Is the Life Safety room style defined?".format(output.linkify(room.Id, room.LookupParameter("Name").AsString())))
        return 0
    
    # print room.Area
    return int(math.ceil(room.Area / room.LookupParameter("Rooms_Occupancy AreaPerPerson").AsDouble ()))


def get_all_calculators(doc):
    all_symbols = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Symbol.FamilyName == "Stair Life Safety Calculator", all_symbols)


def get_all_calcuator_types(doc):
    all_symbol_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
    return filter(lambda x: x.FamilyName == "Stair Life Safety Calculator", all_symbol_types)


def get_calculators_by_level(doc, level_name):
    # print level_name

    # for x in get_all_calculators():
        
    #     print x.LookupParameter("Level_Name").AsString()
    # for para in get_all_calculators()[0].Parameters:
    #     print para.Definition.Name
    return filter(lambda x: x.LookupParameter("Level_Name").AsString() == level_name, get_all_calculators(doc))


def update_stair_capacity_calculator(doc, auto_mode = False, show_log = True):
    if not auto_mode:
        options = ["Hide Calculators on sheet", "Show Calculators on sheet"]
        from EnneadTab.REVIT import REVIT_FORMS
        res = REVIT_FORMS.dialogue(main_text = "How to handle the Stair Capacity Calculator graphic?", options = options)
        will_show = res == options[1]
    
        
    

    
    t = DB.Transaction(doc, __title__)
    t.Start()
    pass

    # get all the room of each level.
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()
    level_dict = dict()
    for room in all_rooms:
        if room.Level.Name not in level_dict:
            level_dict[room.Level.Name] = list()
        level_dict[room.Level.Name].append(room)
        
    # for level_name , level_list in level_dict.items():
    #     print (level_name)
    #     print (level_list)
    
    # for each level, get the total of egress requirement.
    for level_name , level_list in level_dict.items():
        if show_log:
            output.print_md("---")
            print ("\n\nWorking on {}".format(level_name))
        
        total_egress_requirement = 0
        for room in level_list:
            total_egress_requirement += get_room_final_capacity(room, show_log)
        
        if show_log:
            print ("total egress requirement in this level = {}".format(total_egress_requirement))
        
        # find all the calculator type of this level, 
        # divide the total requirement by the number of the calculator., 
        # roundup the result and feed to calulator's instance parameter.
        unique_stair_calculators = set()
        for calculator in get_calculators_by_level(doc, level_name):
            # print calculator.Symbol.LookupParameter("Type Name").AsString()
            unique_stair_calculators.add(calculator.Symbol.LookupParameter("Type Name").AsString())
        unique_stair_calculators_count = len(list(unique_stair_calculators))
        if show_log:
            print ("unique calculator count in this level  = {}".format(unique_stair_calculators_count))
        
        
        each_stair_capacity_requirement = math.ceil(total_egress_requirement / float(unique_stair_calculators_count))
        
        for i, calculator in enumerate(EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(get_calculators_by_level(doc, level_name))):
            
            calculator.LookupParameter("Stair Required Capacity").Set(each_stair_capacity_requirement)
            calculator.LookupParameter("Door Required Capacity").Set(each_stair_capacity_requirement)
            if not auto_mode:
                calculator.LookupParameter("show_calculator").Set(will_show)
        
        
        # make sure all the stairID is matching the type name
        for type in EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(get_all_calcuator_types(doc)):
            type_name =  type.LookupParameter("Type Name").AsString()
            type.LookupParameter("Egress Id").Set(type_name)

        
    t.Commit()
    
    if show_log:
        output.print_md("---")
        print ("\n\nAll calculator data updated.")
    
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
    update_stair_capacity_calculator(doc)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)



