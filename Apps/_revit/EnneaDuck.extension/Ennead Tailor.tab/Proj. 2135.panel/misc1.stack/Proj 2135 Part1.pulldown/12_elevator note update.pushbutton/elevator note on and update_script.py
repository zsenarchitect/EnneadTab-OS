__doc__ = "Turn on elevator notes about the base level and top level of the elevator model, its usage mark, and when was the last time this scheck was run."
__title__ = "12_turn on elevator note and update data"

from pyrevit import forms, DB, revit, script
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import time


def update_timestamp(elevator):

    user_name = revit.doc.Application.Username
    localtime = time.asctime( time.localtime(time.time()) ).replace(":","-")

    timestamp = "Script Last Run By " + user_name + "\nat local time " + localtime
    elevator.LookupParameter("TimeStamp").Set(timestamp)




def print_all_para(element):
    print("^"*10)
    for para in element.Parameters:
        print(para.Definition.Name)

    print("/"*10)

def print_element_link(el):
    print("{}".format(output.linkify(el.Id, title = "Go to elevator")))

def get_all_elevators():
    all_symbol_types =  DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_SpecialityEquipment).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Symbol.Family.Name == "Elevator_Main", all_symbol_types)



def set_data_to_elevator(elevator):
    global hide_note
    print("*"*20)
    #print_all_para(elevator)
    level_base = revit.doc.GetElement(elevator.LookupParameter("Base Level").AsElementId()).Name
    level_top = revit.doc.GetElement(elevator.LookupParameter("Top Level").AsElementId()).Name
    """
    level_base = elevator.Parameter[DB.BuiltInParameter.FAMILY_BASE_LEVEL_PARAM].AsString()
    level_top = elevator.Parameter[DB.BuiltInParameter.FAMILY_TOP_LEVEL_PARAM].AsString()
    """

    description = elevator.LookupParameter("Elevator ID").AsString()

    note = "{}:\n{}\n{}".format(description, level_base, level_top)
    print(note)
    print_element_link(elevator)

    elevator.LookupParameter("Comments").Set("{} --> {}".format(level_base, level_top))
    elevator.LookupParameter("Elevator Note").Set(note)
    elevator.LookupParameter("show_note").Set(not(hide_note))
    update_timestamp(elevator)


################## main code below #####################
output = script.get_output()
output.close_others()

#elevators = get_all_elevators()

with revit.Transaction("update elevator note"):
    #rename_schedule()
    res = forms.alert("i want to [...] the elevator notes", options = ["show", "hide"])
    if res == "hide":
        hide_note = True
    else:
        hide_note = False
    map(set_data_to_elevator, get_all_elevators())
