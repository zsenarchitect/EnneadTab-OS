#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Make sure all door with Egress Id is accounted in the calculator collection."
__title__ = "(Depreciated)Format Egress Doors"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
import math
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore

from collections import defaultdict
try:
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
except:
    pass


def get_all_calculator_of_exit(doc):
    
    all_symbol_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
    calculator_types =  filter(lambda x: x.FamilyName == "Stair Life Safety Calculator", all_symbol_types)
    return filter(lambda x: "EXIT" in x.LookupParameter("Type Name").AsString(), calculator_types)

def get_door_width(door):
    try:
        return door.LookupParameter("Width").AsDouble()
    except:
        return door.Symbol.LookupParameter("Width").AsDouble()

class DoorData:
    id_collection = dict()
    
    def __init__(self, egress_id):
        self.egress_id = egress_id
        self.count = 0
        self.collection = []
        self.occupancy_load = 0
        self.total_width = 0

    @classmethod
    def get_data(cls, egress_id):
        if egress_id in cls.id_collection:
            return cls.id_collection[egress_id]
        instance = DoorData(egress_id)
        cls.id_collection[egress_id] = instance
        return instance

        
    def add_door(self, door):
        self.count += 1
        self.collection.append(door)
        self.total_width += get_door_width(door)
        
    def add_room_occupancy_load(self, room):
        
        self.occupancy_load += get_room_final_capacity(room)


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

def format_new_egress_doors(doc, show_log = True):
    pass


    all_doors = DB.FilteredElementCollector(doc).OfCategory(
        DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

    all_doors = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_doors)

    unique_door_id = set()
    # door_width_dict = defaultdict(int)
    # door_count_dict = defaultdict(int)
    for door in all_doors:

        
        para = door.LookupParameter("Egress_Id")
        if not para.HasValue or para.AsString() == "":
            continue
        
        egress_id = para.AsString()
        effective_width = get_door_width(door)
        if show_log:
            print ("door {},  width = {}".format(output.linkify(door.Id, title = egress_id),   effective_width))
        unique_door_id.add(egress_id)
        
        # door_width_dict[egress_id] += effective_width
        # door_count_dict[egress_id] += 1
        DoorData.get_data(egress_id).add_door(door)
        
    gather_egress_target(doc, show_log)
    
    
    t = DB.Transaction(doc, __title__)
    t.Start()  
        
    missing_calculators = list(unique_door_id - set([x.LookupParameter("Type Name").AsString() for x in get_all_calculator_of_exit(doc)]))
    if len(missing_calculators) != 0:
        print ("Those exit door has no calculator setup: Ask Sen Zhang for help.")
        for x in missing_calculators:
            print (x)
            
    for id in sorted(DoorData.id_collection.keys()):
        if show_log:
            print ("{} : total width = {}ft with {} doors".format(id, 
                                                                DoorData.id_collection[id].total_width, 
                                                                DoorData.id_collection[id].count))

    

        calculator_type = get_calculator_type_by_egress_id(doc, id)
        if not calculator_type:
            print ("No calculator type found for id {}".format(id))
            continue
        calculator_type.LookupParameter("Door Width").Set(DoorData.id_collection[id].total_width)
        
        


       
    t.Commit()
    
    
def get_calculators_by_level(doc, level_name):
    # print level_name

    # for x in get_all_calculators():
        
    #     print x.LookupParameter("Level_Name").AsString()
    # for para in get_all_calculators()[0].Parameters:
    #     print para.Definition.Name
    return filter(lambda x: x.LookupParameter("Level_Name").AsString() == level_name, get_all_calculators(doc))

def get_all_calculators(doc):
    all_symbols = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Symbol.FamilyName == "Stair Life Safety Calculator", all_symbols)

def gather_egress_target(doc, show_log):
    no_target_rooms = []
    for room in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements():
        target = room.LookupParameter("Rooms_EgressTarget").AsString()
 
        if target == "" or target is None:
            no_target_rooms.append(room)
            continue
        if "+" in target:
            target_list = target.split("+")
            target_list = [x.strip() for x in target_list]
        else:
            target_list = [target]
            
        for target in target_list:
            DoorData.get_data(target).add_room_occupancy_load(room)
            
    if len(no_target_rooms) > 0:
        print ("\There are {} rooms have no egress target: ".format(len(no_target_rooms)))
        if show_log:
            for room in no_target_rooms:
                print (output.linkify(room.Id, title = room.LookupParameter("Name").AsString()))
            
    
    
        # calculator.LookupParameter("Door Required Capacity").Set(DoorData.id_collection[id].occupancy_load)
        # calculator.LookupParameter("Stair Required Capacity").Set(DoorData.id_collection[id].occupancy_load)


def get_all_calcuator_types(doc):
    all_symbol_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
    return filter(lambda x: x.FamilyName == "Stair Life Safety Calculator", all_symbol_types)

def get_calculator_type_by_egress_id(doc, id):
    for type in get_all_calcuator_types(doc):
        type_name =  type.LookupParameter("Type Name").AsString()
        if type_name == id:
            return type
        
    # if len(changed_doors) > 0:
    #     print("\nThe {} doors life safety title are updated.".format(len(changed_doors)))
    #     # for door in changed_doors:
    #     #     print(output.linkify(
    #     #         door.Id, title=door.LookupParameter("Name").AsString()))
            
    # if len(bad_doors) > 0:
    #     print("\n\nThe {} doors need attention, they have no life safety style assigned.".format(len(bad_doors)))
    #     # for door in bad_doors:
    #     #     print(output.linkify(
    #     #         door.Id, title=door.LookupParameter("Name").AsString()))
    # else:
    #     if show_log:
    #         print("All look good.")


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
    phase_provider = DB.ParameterValueProvider( DB.ElementId(DB.BuiltInParameter.door_PHASE))
    phase_rule = DB.FilterElementIdRule(phase_provider, DB.FilterNumericEquals(), phase.Id)
    phase_filter = DB.ElementParameterFilter(phase_rule)
    all_doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_doors).WherePasses(phase_filter).WhereElementIsNotElementType().ToElements()
    return all_doors
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    format_new_egress_doors(doc)
    ENNEAD_LOG.use_enneadtab(
        coin_change=20, tool_used=__title__.replace("\n", " "), show_toast=True)


