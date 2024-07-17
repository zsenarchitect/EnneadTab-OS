#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyrevit import forms #
from pyrevit import script #


from EnneadTab.REVIT import REVIT_UNIT
from EnneadTab import NOTIFICATION, ERROR_HANDLE

from Autodesk.Revit import DB # pyright: ignore 


def modify_level_pair(raw_data, level_name, level_gap,is_adding = True):
    if is_adding:
        raw_data.append(level_gap, level_name)
    else:
        for i, existing_level_name in enumerate(raw_data):
            if level_name == existing_level_name:
                raw_data = raw_data[:i-1] + raw_data[i+1:]
                break
    print (raw_data)
    return raw_data

def get_level_data(raw_data):
    prefix = ""

    raw_data_above_ground, raw_data_below_ground = raw_data
    """example of datgrid raw input,  !!!!!!!!! better translate the unit before sending to modeless
    raw_data_above_ground = ["LEVEL 1", 
                            6000,
                            "LEVEL 2", 
                            5500,
                            "LEVEL 3", 
                            5500,
                            "LEVEL 4", 
                            4500,
                            "LEVEL 5", 
                            4500,
                            "MEP LEVEL", 
                            5000,
                            "ROOF LEVEL"]
    """
    level_names_above_ground = raw_data_above_ground[::2]
    level_gap_above_ground = raw_data_above_ground[1::2]
    level_names_below_ground = raw_data_below_ground[::2]
    level_gap_below_ground = raw_data_below_ground[1::2]
    
    
    # level_names_above_ground = ["LEVEL 1", "LEVEL 2", "LEVEL 3", "LEVEL 4", "LEVEL 5", "MEP LEVEL", "ROOF LEVEL"]
    # level_gap_above_ground = [6000,5500,5500,4500,4500, 5000]
    # level_names_below_ground = ["LEVEL B1", "LEVEL B2", "LEVEL B3", "LEVEL B4"]
    # level_gap_below_ground = [6000,5000,5000]
    
    
    level_data = dict()
    level_data["SITE LEVEL"] = -150
    
    current_level_elevation = 0
    for i, name in enumerate(level_names_above_ground):
        level_data[prefix + name] = current_level_elevation
        current_level_elevation += level_gap_above_ground[i]

    
    current_level_elevation = 0
    for i, name in enumerate(level_names_below_ground):
        level_data[prefix + name] = current_level_elevation
        current_level_elevation -= level_gap_below_ground[i]
        
    return level_data

@ERROR_HANDLE.try_catch_error
def create_levels(doc, level_data, prefix):

    is_mm = REVIT_UNIT.is_doc_unit_mm(doc)
    is_ft = REVIT_UNIT.is_doc_unit_feet(doc)
    is_inch = REVIT_UNIT.is_doc_unit_inches(doc)
    
    success_count = 0
    # print titleblock_type_id
    t = DB.Transaction(doc, "Create Levels")
    t.Start()
    for creation_data in level_data:
        print ("trying to create {}{}".format(prefix, creation_data))
        try:
            level = None
            
           
            if is_mm:
                level = DB.Level.Create(doc, REVIT_UNIT.mm_to_internal(creation_data.level_elevation))
            if is_ft:
                level = DB.Level.Create(doc, creation_data.level_elevation)
            if is_inch:
                level = DB.Level.Create(doc, (creation_data.level_elevation)/12)
            
            
        except Exception as e:
            print ("Fail to create <{}{}> becasue {}.".format(prefix,creation_data, e))
        
        if not level:
            print ("Fail to create <{}{}> becasue unit is not typical.".format(prefix, creation_data))
            continue
        
        try:
            level.Name = prefix + creation_data.level_name
            success_count += 1
        except Exception as e:
            print ("Fail to set name of <{}{}> becasue {}.".format(prefix,creation_data, e))
            level.Name = prefix + creation_data.level_name + "_conflict_{}".format(level.Id)
            
            
    t.Commit()
    NOTIFICATION.messenger (main_text =  "Successfully created {} levels.".format(success_count))
    


class LevelDataGrid:
    all_levels = []
    
    
    
    def __init__(self, level_name, level_gap):
        
        self.level_name = level_name
        self.level_gap = level_gap
        self.level_gap_formated = level_gap
        if len(LevelDataGrid.all_levels) == 0:
            self.level_elevation = 0
            return
        
        previous_level = LevelDataGrid.all_levels[-1]
        self.level_elevation = previous_level.level_elevation + previous_level.level_gap

    @classmethod
    def format_display(cls):
        for x in cls.all_levels:
            x.level_gap_formated = x.level_gap
        ranked = sorted(cls.all_levels, key=lambda x: x.level_elevation)
        highest_level = ranked[-1]
        highest_level.level_gap_formated = "---"
        
    @classmethod 
    def add_level(cls, level_gap):
        last_level = cls.all_levels[-1]
        last_level_name = last_level.level_name
        try:
            level_name = last_level_name.split(" ")[0] + " " + str(int(last_level_name.split(" ")[1]) + 1)
        except:
            level_name = forms.ask_for_string("Name of the new level")
        cls.all_levels.append(LevelDataGrid(level_name, level_gap))
        
        cls.format_display()
        
    @classmethod 
    def remove_level(cls):
        if len(cls.all_levels) == 1:
            return
        cls.all_levels.pop()
        
        cls.format_display()
        
        
    def __repr__(self):
        return "<{}: {}>".format(self.level_name, self.level_elevation)




if __name__== "__main__":
    pass