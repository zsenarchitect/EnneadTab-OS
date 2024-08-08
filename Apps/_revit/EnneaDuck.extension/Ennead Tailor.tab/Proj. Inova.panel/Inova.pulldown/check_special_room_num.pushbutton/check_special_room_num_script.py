#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Find room with duplicated BEA room number per phase."
__title__ = "Find dup BEA room number"

from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def get_all_phase():
    all_phase_ids = DB.FilteredElementCollector(doc).OfClass(DB.Phase).ToElementIds ()
    return sorted([ doc.GetElement(phase_id) for phase_id in all_phase_ids], key = lambda x: x.Name)

def select_phase():
    all_phases = get_all_phase()
    if len(all_phases) == 1:
        return all_phases[0]


    selected = forms.SelectFromList.show(all_phases,
                                        multiselect = False,
                                        name_attr = 'Name',
                                        title = "Pick a phase to process.",
                                        button_name = 'Select Phase to Inspect')
    return selected


def get_rooms_in_phase(phase):

    phase_provider = DB.ParameterValueProvider( DB.ElementId(DB.BuiltInParameter.ROOM_PHASE))
    phase_rule = DB.FilterElementIdRule(phase_provider, DB.FilterNumericEquals(), phase.Id)
    phase_filter = DB.ElementParameterFilter(phase_rule)
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WherePasses(phase_filter).WhereElementIsNotElementType().ToElements()
    return all_rooms

def check_special_room_num():
    phase = select_phase()
    if not phase:
        return
    output.print_md("# Phase: {}".format(phase.Name))

    #  get all the rooms
    all_rooms = get_rooms_in_phase(phase)


    # store special numb er in a dict
    data = dict()


    # iterate thru all rooms, if find existing number, then print and alert
    for room in all_rooms:
        room_num = room.LookupParameter("BEA Room Number").AsString()
        if room_num in data:
            data[room_num].append(room.Id)
        else:
            data[room_num] = [room.Id]

    for num, value in data.items():
        if num == "None":
            continue
        
        if len(value) > 1:
            output.print_md("---")
            output.print_md("## BEA Room number: {} has shown up in {} rooms".format(num, len(value)))
            for room_id in value:
                creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, room_id).Creator
                editor = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, room_id).LastChangedBy 
                #print doc.GetElement(room_id)
                room_name = doc.GetElement(room_id).LookupParameter("Name").AsString()
                design_option = doc.GetElement(room_id).DesignOption 
                if design_option:
                    set_name = doc.GetElement(design_option.Parameter[DB.BuiltInParameter.OPTION_SET_ID].AsElementId()).Name
                    design_option_note = "[{}] {}".format(set_name, design_option.Name)
                else:
                    design_option_note = "Main Model"
    
                print("--{}, created by [{}], last edit by [{}]. Design Option = {}".format(output.linkify(room_id, title = room_name), creator, editor, design_option_note))

    print("\n\n\nDone!")
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    check_special_room_num()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)


