#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Based on the special brep defined in Rhino file, highlight specific panel instances in the current document."
__title__ = "Get Special Selection"
from collections import defaultdict
from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument

def get_cloest_panel(pt, all_panel_locations):
    min_distance = 9999999999
    cloest_panel_id = None
    for panel_id, panel_location in all_panel_locations.items():
        
        distance = pt.DistanceTo ( panel_location )
        if distance < min_distance:
            min_distance = distance
            cloest_panel_id = panel_id

    return doc.GetElement(cloest_panel_id)  
       
@EnneadTab.ERROR_HANDLE.try_catch_error()
def get_special_selection():
    
    family_list = ["TYP PANEL",
                   "RFG PANEL",
                   "Tower Corner 1_Flat G",
                   "Tower Corner 2",
                   "TYP TOP PANEL", 
                   "TYP TOP PANEL_Corner 1",
                   "TYP TOP PANEL_Corner 2", 
                   "TYP PANEL@ RFG CUREVE",
                   "TYP PANEL@ RFG CUREVE_CORNER small", 
                   "TYP PANEL@ RFG CUREVE_CORNER large"]
    selected_family = forms.SelectFromList.show(family_list, multiple = False, title = "Pick the family to handle")
    if not selected_family:
        return
    
    
    all_panels = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()
    
    family_count = defaultdict(int)
    def good_family(x):
        if not hasattr(x, "Symbol"):
            return False
        family_name = x.Symbol.Family.Name
        #print family_name
        family_count[family_name] += 1
        
        
        if family_name == selected_family :
            return True
        return False
    
    
    all_panel_locations = dict()
    for panel in all_panels:
        bbox = panel.get_BoundingBox(doc.ActiveView)
        if not bbox:
            continue
        panel_location = (bbox.Max + bbox.Min)/2
        all_panel_locations[panel.Id] = panel_location
    
    data = EnneadTab.DATA_FILE.read_json_as_dict_in_dump_folder("temp_selection_location.json")
    #print data
    if not data:

        EnneadTab.NOTIFICATION.messenger(main_text = "You need to record the panel location in Rhino first ...")
    selection = []

        
        
    for i, value in enumerate(data.values()):
        print ("{}/{} : {}".format(i+1, len(data.values()), value))
        pt = DB.XYZ(EnneadTab.REVIT.REVIT_UNIT.mm_to_internal(float(value[0])),
                    EnneadTab.REVIT.REVIT_UNIT.mm_to_internal(float(value[1])),
                    EnneadTab.REVIT.REVIT_UNIT.mm_to_internal(float(value[2])))
        cloest_panel = get_cloest_panel(pt, all_panel_locations)
        selection.append(cloest_panel)
    
    
    selection = filter(good_family, selection)
    EnneadTab.REVIT.REVIT_SELECTION.set_selection(selection)
    print ("\n\n{} panels selected. Current family filter = {}".format(len(selection), selected_family))
    
    
    print ("\nBelow are all the panels family count that is close to the sample surface in Rhino:")
    for family_name, count in sorted(family_count.items()):
        print ("  - {}: {}".format(family_name, count))

    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
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
    get_special_selection()
    











