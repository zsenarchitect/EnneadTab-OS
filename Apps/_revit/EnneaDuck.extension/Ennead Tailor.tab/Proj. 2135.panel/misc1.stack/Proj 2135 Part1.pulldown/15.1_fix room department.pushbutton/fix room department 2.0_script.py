__doc__ = "Find the room department that is using names other than agreed name list. And attempt to fix it. \n\nName list location: \n\nI:\\2135\\6_Team\\CH\\2022-03-05 Color Scheme\\Room Department Script.txt"
__title__ = "15.1_fix color_room department 2.0"

from pyrevit import forms, DB, revit, script, coreutils

def get_all_rooms():
    return DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

def is_department_in_checklist(room):
    global room_department_checklist
    if room.LookupParameter("Department").AsString() in room_department_checklist:
        return True
    return False


def set_rm_department(room, department):
    global in_group_rm_found
    if room.GroupId.IntegerValue  > 0:
        room_name = room.LookupParameter("Name").AsString()
        if len(room_name) == 0:
            room_name = "N/A"
        current_department = room.LookupParameter("Department").AsString()
        markdown = "skipping room {} becasue it is in group [**{}**]. Name = **{}**, Level = **{}**, Current Department = **{}**, Target Department = **{}**".format(output.linkify(room.Id),revit.doc.GetElement(room.GroupId).Name, room_name, room.Level.Name, current_department, department)
        output.print_md(markdown)
        in_group_rm_found = True
        return
    try:
        room.LookupParameter("Department").Set(department)
    except Exception as e:
        print("*"*10)
        print("skipping room {} ".format(output.linkify(room.Id)))
        print (e)
        print("*"*10)

def try_to_fix_rm(department):

    global room_department_checklist

    target = forms.SelectFromList.show(button_name = "pick a target department", \
                                        context = room_department_checklist, \
                                        multiselect = False,\
                                        title = "[{}]--->?".format(department))

    if target == "<keep as current, make no change>":
        return

    similar_rms = filter(lambda x: x.LookupParameter("Department").AsString() == department, get_all_rooms())
    map(lambda x: set_rm_department(x, target), similar_rms)





def pick_bad_department():
    bad_rms = filter(lambda x: not is_department_in_checklist(x), get_all_rooms())
    """
    bad_departments = []
    for rm in bad_rms:
        department = rm.LookupParameter("Department").AsString()
        if department not in bad_departments:
            bad_departments.append(department)
    """
    bad_departments = list({x.LookupParameter("Department").AsString() for x in bad_rms})
    bad_departments.sort(reverse = True)
    bad_departments.insert(0,"<select me to finish tool>")

    return forms.SelectFromList.show(button_name = "pick a department to fix", \
                                        context = bad_departments, \
                                        multiselect = False,\
                                        title = "i have found those department names not exist in master color pallte")


def get_checklist():
    filepath = r"I:\2135\6_Team\CH\2022-03-05 Color Scheme\Room Department Script.txt"
    with open(filepath) as f:
        lines = f.readlines()
    lines.insert(0, "<keep as current, make no change>")
    return map(lambda x: x.replace("\n",""), lines)
    #return coreutils.read_source_file(filepath)

################## main code below #####################
output = script.get_output()
output.close_others()
in_group_rm_found = False


room_department_checklist = get_checklist()
#print department_checklist



with revit.Transaction("fix room"):

    safety = 0

    while True:
        res = pick_bad_department()
        if res == "<select me to finish tool>":
            break
        if safety > 100:
            break
        safety += 1

        try_to_fix_rm(res)


if in_group_rm_found:
    forms.alert("some room cannot be changed becasue they are in a group. See output window for detail")
    output.show()
    output.set_width(1500)
    output.center()
