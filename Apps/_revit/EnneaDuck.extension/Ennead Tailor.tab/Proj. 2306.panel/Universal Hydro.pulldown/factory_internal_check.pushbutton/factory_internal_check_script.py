#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "All In One Checker"
__title__ = "Factory Internal All-In-One Check"

# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import math
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
try:
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
except:
    pass

class InternalCheck:
    def __init__(self, doc, show_log):
        self.doc = doc
        self.show_log = show_log
        self.all_rooms = []
        self.all_sheets = []
        self.all_areas = []
        self.all_stairs = []
        self.life_safety_calculators = dict() # key = (egress_id, level)



    def run_check(self):
        pass
    
        # chheck all sheets to show in sheetlist, have default print_in_color value
        self.check_sheets()
        
        
        # check all areas Make sure all areas have at least a valid discount data.\n\nMake sure all areas have department data.
        self.check_areas()


        # Make sure all room 'Rooms_$LS_Occupancy Manual' is at-least -1.
        # \n\nAlso transfer the name of the life safety key to the title so you can see it on tags."
        # alert rooms with no life safety style defined.
        # check all rooms shoudl have egress target,   and "Gather the room life safety data from rooms of each level use target list to add occupancy load to each target, and make sure calculator type names == target list names
        self.check_rooms()
        
        # Make sure all egress stair has consistent width on run, and store width data , and  make sure calculator type names == stair names.
        self.check_stairs()

        # check all doors with egressId  and store total width data , and make sure calculator type names == door names.
        self.check_doors()
        
        

        # lets check the current datas
        if self.show_log:
            print ("Milestone data display")
            for data in sorted(EgressData.data_collection.values(), key = lambda x: (x.level, x.egress_id)):
                data.print_data(self.show_log)
        

        #  make sure all calcator type egressId match type name
        self.update_calculator_types()
                
        
        # update calculator data  
        self.update_calculators()
        

    def update_calculator_types(self):
        t = DB.Transaction(self.doc, "update calculator types")
        t.Start()
        all_calc_types = get_all_calcuator_types(self.doc)
        all_calc_types = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_calc_types)
        for type in all_calc_types:
            type_name =  type.LookupParameter("Type Name").AsString()
            if not EgressData.egress_id_exist(type_name):
                print ("{} calcuator exist in revit file but no room is pointing to this egressId. Maybe need to remove this calcuator type".format(type_name))

            if type_name != type.LookupParameter("Egress Id").AsString():
                type.LookupParameter("Egress Id").Set(type_name)
        t.Commit()
        if self.show_log:
            print ("Calculator types updated")
            output.print_md("---")
                
                
    def update_calculators(self):
        t = DB.Transaction(self.doc, "check calculators")
        t.Start()
        for data in sorted(EgressData.data_collection.values(), key = lambda x: (x.level, x.egress_id)):
            # print (data.egress_id)
            calculator_type = get_calculator_type_by_egress_id(self.doc, data.egress_id)
            
            if not calculator_type:
                print ("No calculator type found for egressId:{}, maybe need to create this type.".format(data.egress_id))
                continue
            if not EnneadTab.REVIT.REVIT_SELECTION.is_changable(calculator_type):
                continue
            # push stair width data to calculator type stair width
            # push door width data to calculator type door width
            if data.is_stair:
                calculator_type.LookupParameter("Stair Width").Set(data.total_width)
            else:
                calculator_type.LookupParameter("Door Width").Set(data.total_width)
                
                
            # push total occupancyload of (egreeid,level) and feed into the Stair Capacity Calculator instance (look by (egreeid,level)) for capacity required."
            calculators = get_calculators_by_key(self.doc, data.level,data.egress_id)
            calculators = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(calculators)
            for calculator in calculators:
                calculator.LookupParameter("Stair Required Capacity").Set(data.occupancy_load)
                calculator.LookupParameter("Door Required Capacity").Set(data.occupancy_load)
                
        t.Commit()
        if self.show_log:
            print ("Calculators updated")
            output.print_md("---")
        
    def check_sheets(self):
        
        t = DB.Transaction(self.doc, "check sheets")
        t.Start()
        key_para = "Print_In_Color"
        all_sheets = DB.FilteredElementCollector(self.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
        all_sheets = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_sheets)
        
        all_sheets = list(all_sheets)
        all_sheets.sort(key = lambda x: x.SheetNumber)

        bad_sheets = set()
        for sheet in all_sheets:
            para = sheet.LookupParameter(key_para)
            if not para:
                continue
            if not para.HasValue:
                print ("Assign default Print In Color value at sheet:{}-{}".format(sheet.SheetNumber, sheet.Name))
                
                para.Set(0)
                bad_sheets.add(sheet)

            if not sheet.LookupParameter("Appears In Sheet List").AsInteger():
                sheet.LookupParameter("Appears In Sheet List").Set(1)
                bad_sheets.add(sheet)
            
    
        t.Commit()


        if len(bad_sheets) >0:
            print ("\n\n{} sheets are corrected:".format(len(bad_sheets)))
            if self.show_log:
                for sheet in bad_sheets:
                    print (output.linkify(sheet.Id, title = sheet.SheetNumber + " - " + sheet.Name))
        else:
            if self.show_log:
                print ("Sheets All look good.") 
                output.print_md("---")
            

    def check_areas(self):
    
        t = DB.Transaction(self.doc, "check areas")
        t.Start()
        all_areas = DB.FilteredElementCollector(self.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
        all_areas = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_areas)
        
        
        bad_areas = set()
        for area in all_areas:
            # fix area that does not have discount factor data
            para = area.LookupParameter("Discount Factor")
            if not para.HasValue:
                para.Set(1.0)
                bad_areas.add(area)


            # highlight area that has not department data
            para = area.LookupParameter("Area Department")
            if not para.HasValue:
                para.Set("Department Undefined")
                bad_areas.add(area)
        t.Commit()


        if len(bad_areas) >0:
            print ("\n\n{} areas are corrected:".format(len(bad_areas)))
            if self.show_log:
                for area in bad_areas:
                    print (output.linkify(area.Id, title = area.LookupParameter("Name").AsString()))
        else:
            if self.show_log:
                print ("Areas All look good.") 
                output.print_md("---")
            
    def check_rooms(self):
        t = DB.Transaction(self.doc, __title__)
        t.Start()
        all_rooms = DB.FilteredElementCollector(self.doc).OfCategory(
            DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

        # all_rooms = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_rooms)
        bad_rooms_no_safety_style = set()
        bad_rooms_no_target = set()
        changed_rooms = set()
        def check_room_life_safety_basic_condition(room):
            is_changable = EnneadTab.REVIT.REVIT_SELECTION.is_changable(room)

            # make sure this parameter has at least -1.
            para = room.LookupParameter("Rooms_Occupancy Manual")
            if not para.HasValue and is_changable:
                para.Set(-1)
                bad_rooms_no_safety_style.add(room)

            # update the title
            room_style_id = room.LookupParameter("Life Safety").AsElementId()
            if room_style_id.IntegerValue == -1:
                if self.show_log:
                    print("This room has no life safety style defined--->{}".format(
                    output.linkify(room.Id, title=room.LookupParameter("Name").AsString())))
                style_name = "--No Life Safety Style Defined--"
                bad_rooms_no_safety_style.add(room)

            else:
                room_style = self.doc.GetElement(room_style_id)
                style_name = room_style.Name

            if room.LookupParameter("Rooms_Occupancy Style Title").AsString() != style_name:
                if is_changable:
                    room.LookupParameter("Rooms_Occupancy Style Title").Set(style_name)
                changed_rooms.add(room)
                
                
            egress_target = room.LookupParameter("Rooms_EgressTarget").AsString()
            if egress_target == "" or egress_target is None or egress_target == "--No Egress Target--":
                if self.show_log:
                    print("Room:{} has no egress target".format(output.linkify(room.Id, 
                                                                            title = room.LookupParameter("Name").AsString()
                                                                            )
                                                                )
                        )
                if egress_target !=  "--No Egress Target--" and is_changable:
                    room.LookupParameter("Rooms_EgressTarget").Set("--No Egress Target--")
                bad_rooms_no_target.add(room)
     
        

        for room in all_rooms:
            check_room_life_safety_basic_condition(room)
            
            self.gather_room_life_safety_data(room)
            

        t.Commit()

        if len(changed_rooms) > 0:
            print("\nThe {} rooms life safety title are updated.".format(len(changed_rooms)))
            for i, room in enumerate(changed_rooms):
                print("{}:{}".format(i + 1, output.linkify(room.Id, title = room.LookupParameter("Name").AsString())))
                
        if len(bad_rooms_no_safety_style) > 0:
            print("\n\nThe {} rooms need attention, they have no life safety style assigned.".format(len(bad_rooms_no_safety_style)))
        if len(bad_rooms_no_target) > 0:
            print("\n\nThe {} rooms need attention, they have no egress target assigned.".format(len(bad_rooms_no_target)))
        else:
            if self.show_log:
                print("All Rooms look good.")  
                output.print_md("---")
                
                
                     
    def gather_room_life_safety_data(self, room):
        
        target = room.LookupParameter("Rooms_EgressTarget").AsString()
        if target == "" or target is None:
            target = "--No Egress Target--"
            print ("{}Target not exist".format(output.linkify(room.Id, title = room.LookupParameter("Name").AsString())))
            return
        
        if "+" in target:
            target_list = target.split("+")
            target_list = [x.strip() for x in target_list]
        else:
            target_list = [target]
            
        #print ("{}Target list: {}".format(output.linkify(room.Id, title = room.LookupParameter("Name").AsString()),target_list))
        for target in target_list:
            # if "EXIT B" in target:
            #     print ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if "exit" in target.lower():
                if room.Level.Name != "LEVEL 1":
                    print ("This room {} is not in level 1 but targeting an exit, please check".format(output.linkify(room.Id, title = room.LookupParameter("Name").AsString())))
                DoorData.get_data(room.Level.Name, target).add_room_occupancy_load(room, branch_count = len(target_list))
                # print ("DOOR+{}Target {}".format(output.linkify(room.Id, title = room.LookupParameter("Name").AsString()),target))
            elif "stair" in target.lower():
                StairData.get_data( room.Level.Name, target).add_room_occupancy_load(room, branch_count = len(target_list))
                # print ("STAIR+{}Target {}".format(output.linkify(room.Id, title = room.LookupParameter("Name").AsString()),target))

    def check_stairs(self):
        t = DB.Transaction(self.doc, "Check stairs")
        t.Start()

        all_stairs = DB.FilteredElementCollector(self.doc).OfCategory(DB.BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()
        # all_stairs = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_stairs)
        #  do not need to filter editbale because i am collecting data

        

        for stair in all_stairs:
            stair_id = stair.LookupParameter("Egress_Id").AsString()
            if not stair_id:
                print ("\n!!!!!Checking no egress Id stair: {}. Talk to Sen Zhang for details for what it means.".format(output.linkify(stair.Id)))
            else:
                pass
                    
                    
            # update the stair width data
            #print (StairData.data_collection)
            for data in StairData.data_collection.values():
                if data.egress_id == stair_id:
                    data.add_stair(stair)

 
        t.Commit()
        if self.show_log:
            print("All Stairs look good.")  
            output.print_md("---")

    def check_doors(self):
        all_doors = list(DB.FilteredElementCollector(self.doc).OfCategory(
        DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements())
        # for door in all_doors:
        #     if door.LookupParameter("Comments").AsString() == "aaa":
        #         print output.linkify(door.Id)
        
        
        # all_panels = DB.FilteredElementCollector(self.doc).OfCategory(
        # DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()
        # panel_doors = filter(lambda x:  x.LookupParameter("Egress_Id") is not None, all_panels)
        # print panel_doors
        
        # all_doors.extend(panel_doors)
        
        all_doors = filter(lambda door:  door.LookupParameter("Egress_Id").HasValue and door.LookupParameter("Egress_Id").AsString() != "", all_doors)
        
        # for door in all_doors:
        #     if door.LookupParameter("Egress_Id").AsString() == "EXIT B":
        #         print output.linkify(door.Id)
        # all_doors = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_doors)
        #  do not need to filter editbale because i am collecting data


        for door in all_doors:

            
            para = door.LookupParameter("Egress_Id")

            
            egress_id = para.AsString()
            
            # if egress_id == "EXIT B":
            #     print ("*****************************")
            #     print (output.linkify(door.Id))
            
            if self.doc.GetElement(door.LevelId).Name != "LEVEL 1":
                print ("This door {} is not in level 1, should not be part of the egress, please check".format(output.linkify(door.Id)))

            # update the exist door width data
            for data in DoorData.data_collection.values():

                if data.egress_id == egress_id:
                    data.add_door(door)
                    
        if self.show_log:
            print("All Egress Doors look good.")  
            output.print_md("---")

class EgressData:
    data_collection = dict()
    
    @classmethod
    def egress_id_exist(cls, test_id):
        for data in cls.data_collection.values():
            if data.egress_id == test_id:
                return True
        return False
    
    @property
    def is_stair(self):
        return "stair" in self.egress_id.lower()
    
    def __init__(self, level_name, egress_id):
        self.level = level_name
        self.egress_id = egress_id

        self.revit_obj_collection = []
        self.occupancy_load = 0
        self.total_width = 0
        self.source_rooms = []

    @classmethod
    def get_data(cls, level_name, egress_id):
        key = (level_name, egress_id)
        if key in cls.data_collection:
            return cls.data_collection[key]
        if "stair" in egress_id.lower():
            
            instance = StairData(level_name, egress_id)
        else:
             instance = DoorData(level_name, egress_id)
        cls.data_collection[key] = instance
        return instance
    
    def add_room_occupancy_load(self, room, branch_count): 
        self.source_rooms.append(room)
        room_final_capacity = get_room_final_capacity(room)
        # only add occpancy portioned to this data
        self.occupancy_load += int(math.ceil(room_final_capacity / float(branch_count)))
        
    def print_data(self, show_log):
        if show_log or len(self.revit_obj_collection) == 0:
            print ("\n{} {} has {} items with {} occupancy capacity and {}feet total width".format(self.level, self.egress_id, len(self.revit_obj_collection), self.occupancy_load, self.total_width))
        if len(self.revit_obj_collection) > 0:
            if show_log:
                print ("The items are: ")
                for item in self.revit_obj_collection:
                    print (output.linkify(item.Id, title = str(item.GetType())))
        else:
            print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nNo item with this egress id {}. There are rooms point to this egress adress but no revit object is actually using this address.Talk to Sen Zhang for details for what it means.".format(self.egress_id))
            if show_log:
                for room in self.source_rooms:
                    print (output.linkify(room.Id, title = room.LookupParameter("Name").AsString()))


class DoorData(EgressData):

    def add_door(self, door):

        self.revit_obj_collection.append(door)
        self.total_width += get_door_width(door)
        
class StairData(EgressData):
    def add_stair(self, stair):
        
        self.revit_obj_collection.append(stair)
        if len(self.revit_obj_collection) > 1:
            print ("This should not have more than one stair with this egreeId {} , please check".format(self.egress_id))
            if self.show_log:
                for stair in self.revit_obj_collection:
                    print (output.linkify(stair.Id))
        self.total_width = get_stair_width(stair)

def get_room_final_capacity(room):

    # ignore rooms whose AreaPerPerson is negative
    if room.LookupParameter("Rooms_Occupancy AreaPerPerson").AsDouble() < 0:
        return 0
    
    # pioritise manual override
    if room.LookupParameter("Rooms_Occupancy Manual").AsInteger() >= 0:
        return room.LookupParameter("Rooms_Occupancy Manual").AsInteger()
        
    # print room.Area
    return int(math.ceil(room.Area / room.LookupParameter("Rooms_Occupancy AreaPerPerson").AsDouble ()))


def get_door_width(door):
    try:
        return door.LookupParameter("Width").AsDouble()
    except:
        return door.Symbol.LookupParameter("Width").AsDouble()
    
def get_stair_width(stair):
    runs = [stair.Document.GetElement(x) for x in stair.GetStairsRuns()]
    
    max_width = runs[0].ActualRunWidth
    for run in runs:
        if not  run.ActualRunWidth == max_width:
            print( "--This stair has variring  run width--->{}. Talk to Sen Zhang to understand what it means.".format(output.linkify(run.Id)))
    return max_width
    



def get_all_calculators(doc):
    all_symbols = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Symbol.FamilyName == "Stair Life Safety Calculator", all_symbols)


def get_all_calcuator_types(doc):
    all_symbol_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
    return filter(lambda x: x.FamilyName == "Stair Life Safety Calculator", all_symbol_types)


def get_calculators_by_key(doc, level_name, egress_id):

    return filter(lambda x: x.LookupParameter("Level_Name").AsString() == level_name and x.Symbol.LookupParameter("Egress Id").AsString() == egress_id, get_all_calculators(doc))

def get_calculator_type_by_egress_id(doc, egress_id):

    list =  filter(lambda x: x.LookupParameter("Egress Id").AsString() == egress_id, get_all_calcuator_types(doc))
    if len(list) > 0:
        return list[0]
    return None





@EnneadTab.ERROR_HANDLE.try_catch_error()
def factory_internal_check(doc, show_log):
    InternalCheck(doc, show_log).run_check()
    

  
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    factory_internal_check(doc, show_log = True)
    





