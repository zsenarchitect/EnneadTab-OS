__doc__ = "This gives you ability to remove rooms and areas that is not placed \
in the file to increase document accuracy.\n\nUnbounded/redundent area and rooms\
 will be checked BUT NOT DELETED SO YOU CAN MAKE THE FINAL DECISION.(Mostly likely they are still important for you.)\n\nYou also have\
the option to check room status by phase."
__title__ = "Remove Not Placed\nArea and Rooms"
__tip__ = True
from pyrevit import forms,  script
from EA_UTILITY import dialogue
from Autodesk.Revit import DB # pyright: ignore

from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

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


def get_element_phase(element):
    return
    para_id = DB.BuiltInParameter.ROOM_PHASE
    phase = element.Parameter[para_id].AsString()
    print(phase)
    return
    for para in element.Parameters:
        print(para.Definition.Name)
        if "phase" in  para.Definition.Name.lower():
            print(para.Definition.Name)
            print(para.AsString())
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(element.LookupParameter("Phase").AsString())
    print("@@@")
    all_phase_ids = DB.FilteredElementCollector(doc).OfClass(DB.Phase).ToElementIds ()
    for phase_id in all_phase_ids:
        print(doc.GetElement(phase_id).Name)
        print(element.GetPhaseStatus(phase_id))
        if element.GetPhaseStatus(phase_id) == DB.ElementOnPhaseStatus.New:
            return "Phase = {}".format(doc.GetElement(phase_id).Name)
    return



    phase = doc.GetElement(element.CreatedPhaseId)
    if phase:
        phase_creation = phase.Name
    else:
        phase_creation = "N/A"


    phase = doc.GetElement(element.DemolishedPhaseId)
    if phase:
        phase_demolision = phase.Name
    else:
        phase_demolision = "N/A"

    if phase_creation == "N/A" and phase_demolision == "N/A":

        para_id = DB.BuiltInParameter.ROOM_PHASE
        phase = element.Parameter[para_id].AsString()
        print(element.Parameter[para_id].AsString())
        print(element.Parameter[para_id].ToString())
        if phase:
            return "Phase = {}".format(phase)
        else:
            return "Phase = N/A"
    return "Phase Created = {}, Phase Demolished = {}".format(phase_creation, phase_demolision)


################## main code below #####################



@ERROR_HANDLE.try_catch_error
def main():
    phase = select_phase()
    if not phase:
        return


    delete_not_placed_areas()
    delete_not_placed_rooms(phase)
    find_non_close_or_redundent_room(phase)
    find_non_close_or_redundent_area()
    find_empty_area_department()

def delete_not_placed_areas():
    all_areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    t = DB.Transaction(doc, "Delete Not Placed area")
    t.Start()
    count = 0
    nega_count = 0
    for area in all_areas:
        if area.Location == None and area.Area == 0:
            doc.Delete(area.Id)
            continue
            count += 1

        if area.Area < 0:
            print("this area has negative area. Area Scheme = {}, Level = {}, area name = {}----{}".format(area.AreaScheme.Name,  doc.GetElement(area.LevelId).Name,area.LookupParameter("Name").AsString(), output.linkify(area.Id, title = "Select Area")))
            nega_count += 1
    t.Commit()

    if count > 0:
        dialogue(main_text = "{} not placed areas are removed from project.".format(count))

    if nega_count > 0:
        dialogue(main_text = "{} negative area in projects".format(nega_count))


def delete_not_placed_rooms(phase):
    all_rooms = get_rooms_in_phase(phase)
    t = DB.Transaction(doc,"Delete Not Placed rooms")
    t.Start()
    count = 0
    for room in all_rooms:
        if room.Location == None and room.Area == 0:
            doc.Delete(room.Id)
            count += 1
    t.Commit()

    if count > 0:
        output.insert_divider()
        print("*"*100)
        dialogue(main_text = "{} not placed rooms are removed from project.".format(count))


def find_non_close_or_redundent_room(phase):
    all_rooms = get_rooms_in_phase(phase)
    count = 0
    open_rooms = []
    for room in all_rooms:
        if room.Area == 0:
            count += 1
            open_rooms.append(room)
    if count > 0:
        output.insert_divider()
        print("*"*100)
        output.print_md("Inspecting on phase <**{}**>".format(phase.Name))

        dialogue(main_text = "{} not enclosed room or redundent room still in the project.".format(count), icon = "warning")
        for room in open_rooms:
            #print area.LookupParameter("Area").AsValueString() ### is this equal to redundent or not enclosed?
            #print area.Perimeter
            #print area.Geometry[DB.Options()]
            print("not enclosed room or redundent room. Phase = {}\nLevel = {}, room department = {}, room name = {}----{}".format( phase.Name,
                                                                                                                            doc.GetElement(room.LevelId).Name,
                                                                                                                            room.LookupParameter("Department").AsString(),
                                                                                                                            room.LookupParameter("Name").AsString(),
                                                                                                                            output.linkify(room.Id, title = "Select Room")))
    else:
        dialogue(main_text = "no non-enclose or redundent Room found.")


def find_non_close_or_redundent_area():
    all_areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    count = 0
    open_areas = []
    for area in all_areas:
        if area.Area == 0:
            count += 1
            open_areas.append(area)
    if count > 0:
        output.insert_divider()
        print("*"*100)

        dialogue(main_text = "{} not enclosed areas or redundent area still in the project.".format(count), icon = "warning")
        for area in open_areas:
            #print area.LookupParameter("Area").AsValueString() ### is this equal to redundent or not enclosed?
            #print area.Perimeter
            #print area.Geometry[DB.Options()]
            area_department = area.LookupParameter("Area Department").AsString() if area.LookupParameter("Area Department") else "N/A"
            print("not enclosed area or redundent area. {}\nArea Scheme = {}, Level = {}, area department = {}, area name = {}----{}".format(get_element_phase(area),
                                                                                                                                            area.AreaScheme.Name,
                                                                                                                                            doc.GetElement(area.LevelId).Name,
                                                                                                                                            area_department,area.LookupParameter("Name").AsString(),
                                                                                                                                            output.linkify(area.Id, title = "Select Area")))
    else:
        dialogue(main_text = "no non-enclose or redundent area found.")


def find_empty_area_department():
    return
    output.insert_divider()
    print("*"*100)
    all_areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()

    count = 0
    for area in all_areas:
        if area.AreaScheme.Name != "Gross Building":
            continue
        if area.LookupParameter("Area Department").AsString() == None:

            print("this area has no area department assignemted to it. Area Scheme = {}, Level = {}, area name = {}----{}".format(area.AreaScheme.Name,  doc.GetElement(area.LevelId).Name,area.LookupParameter("Name").AsString(), output.linkify(area.Id, title = "Select Area")))
            count += 1
    if count > 0:
        dialogue(main_text = "{} area has empty area department value in gross buiilding area scheme. See output window for detail".format(count), icon = "warning")
    else:
        dialogue(main_text = "no empty area department value found")




if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    main()
    #get_rooms_in_phase(phase_name = "Learning Content")
    import ENNEAD_LOG
    ENNEAD_LOG.use_enneadtab(coin_change = 30, tool_used = __title__.replace("\n", " "), show_toast = True)
    # output.center()
    output.set_width(1100)
    output.set_height(800)
