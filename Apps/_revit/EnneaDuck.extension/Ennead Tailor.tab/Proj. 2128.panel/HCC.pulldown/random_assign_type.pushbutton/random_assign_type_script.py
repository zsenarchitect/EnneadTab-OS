import random

import clr
from Autodesk.Revit import DB # pyright: ignore
from pyrevit import script
from pyrevit import forms

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

__title__ = "Randomly Reduce Panel Selection to 5 pack, requested by Chiwhei"
__doc__ = 'Randomly deselect from selection input.'


doc = __revit__.ActiveUIDocument.Document # pyright: ignore

TYPE_NAMES = ["A1",
              "C1",
              "D2",
              "D4",
              "D7"]

FAMILY_NAME = "CWPL-Fluted Panel_Single Flute"


def get_type_by_name(type_name):
    # all_types = doc.PanelTypes
    # all_types = DB.FilteredElementCollector(doc).OfClass(DB.PanelType).ToElements()
    all_types = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol).ToElements()
    # print all_types
    # for x in dir(all_types[0]):
    #     print x

    for family_type in all_types :
        # print (family_type.FamilyName)
        
        # print (family_type.LookupParameter("Type Name").AsString())
        if family_type.FamilyName != FAMILY_NAME:
            continue
        if family_type.LookupParameter("Type Name").AsString() == type_name:
            return family_type
    else:
        return family_type
        
        
@EnneadTab.ERROR_HANDLE.try_catch_error()
def main():

    selection = EnneadTab.REVIT.REVIT_SELECTION.get_selection()
    if not selection:
        EnneadTab.NOTIFICATION.messenger(main_text = "Need to select some panels..")
        return
    selection = [x for x in selection if x.Category.Name == "Curtain Panels"]
    if len(selection) ==0:
        EnneadTab.NOTIFICATION.messenger(main_text = "Need curtain panels")
        return
    
    type_map = {i:get_type_by_name(x) for i,x in enumerate(TYPE_NAMES)}
    
    
    opts = ["Totally random",
            "Vertical random",
            "Diagonally layout"]
    res = EnneadTab.REVIT.REVIT_FORMS.dialogue(options = opts)
    if not res:
        return
    if res == opts[0]:
        total_random(selection, type_map)
    elif res == opts[1]:
        vertical_random(selection, type_map)
        
    elif res == opts[2]:
        diagonal_random(selection, type_map)
        
def vertical_random(selection,type_map):
    v_map = dict()
    t = DB.Transaction(doc, "Random Vertical")
    t.Start()
    for panel in selection:
        
        u_grid_id = clr.StrongBox[DB.ElementId](DB.ElementId(1))
        v_grid_id = clr.StrongBox[DB.ElementId](DB.ElementId(2))
        panel.GetRefGridLines (u_grid_id, v_grid_id)
        # print (output.linkify(u_grid_id))
        # print (output.linkify(v_grid_id))

        if v_grid_id.IntegerValue not in v_map:
            v_map[v_grid_id.IntegerValue] = random.sample(type_map.values(), 1)[0]
        panel.Symbol = v_map.get(v_grid_id.IntegerValue,None)
        
    t.Commit()
    # print (v_map)
    EnneadTab.NOTIFICATION.messenger(main_text = "Vertically random divide")

def diagonal_random(selection, type_map):

    order_offset = forms.ask_for_number_slider(default=0,
                                               min=0,max=4,
                                               prompt="layout pattern offset?\nThis offset will apply to every wall used,\nso selectively pick panels if you want to fine tune\nalignment on one of the wall.",
                                               title="Random Diagonal fine tuning.")
    if not order_offset:
        return
    
    wall_dict = dict()
    walls = list(set([x.Host for x in selection]))
    for wall in walls:
        temp_dict = {}
        
        temp_dict["u_order"] = [x.IntegerValue for x in wall.CurtainGrid.GetUGridLineIds()]
        temp_dict["v_order"] = [x.IntegerValue for x in wall.CurtainGrid.GetVGridLineIds()]
        wall_dict[wall.Id] = temp_dict
            
    
    t = DB.Transaction(doc, "Random Diagonal")
    t.Start()
    for panel in selection:
        
        u_grid_id = clr.StrongBox[DB.ElementId](DB.ElementId(1))
        v_grid_id = clr.StrongBox[DB.ElementId](DB.ElementId(2))
        panel.GetRefGridLines (u_grid_id, v_grid_id)
        # print (output.linkify(u_grid_id))
        # print (output.linkify(v_grid_id))

        
        u_order = wall_dict[panel.Host.Id]["u_order"].index(u_grid_id.IntegerValue) + 1 if u_grid_id.IntegerValue != -1 else 0
        v_order = wall_dict[panel.Host.Id]["v_order"].index(v_grid_id.IntegerValue) + 1 if v_grid_id.IntegerValue != -1 else 0
        
        u_order = u_order % len(type_map)
        v_order = v_order % len(type_map)
        
        picker_order = (len(type_map) + (v_order - u_order) + order_offset) % len(type_map)
        
        
        panel.Symbol = type_map.get(picker_order,None)
    t.Commit()
    EnneadTab.NOTIFICATION.messenger(main_text = "Diagnoally random divide")
    
    
def total_random(selection, type_map):
    random.shuffle(selection)
    group_count = len(TYPE_NAMES)
    
    packs = [selection[i::group_count] for i in range(group_count)]
    

    t = DB.Transaction(doc, "Random packing group")
    t.Start()
    for i, pack in enumerate(packs):
        for panel in pack:
            # print panel
            # print panel.Symbol.FamilyName, panel.Symbol.LookupParameter("Type Name").AsString()
            # panel.PanelType = type_map[i]
            panel.Symbol = type_map[i]
            
    
    t.Commit()
    
    
    EnneadTab.NOTIFICATION.messenger(main_text = "Divided to {} group packs".format(group_count))
        


############################################
output = script.get_output()
output.close_others()
if __name__ == "__main__":
    main()

