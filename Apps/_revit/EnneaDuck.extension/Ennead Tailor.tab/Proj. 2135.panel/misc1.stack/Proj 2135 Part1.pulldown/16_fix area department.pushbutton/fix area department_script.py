__doc__ = "If area department is not part of user allowed list, find them and replace them."
__title__ = "16_fix color_area department"

from pyrevit import forms, DB, revit, script

def get_all_areas():
    areas = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.AreaScheme.Name == "Gross Building", areas)

def is_department_in_checklist(area):
    #global area_department_checklist
    if area.LookupParameter("Area Department").AsString() in area_department_checklist:
        return True
    return False


def set_area_department(area, department):
    global in_group_area_found
    if area.GroupId.IntegerValue  > 0:
        area_name = area.LookupParameter("Name").AsString()
        if len(area_name) == 0:
            area_name = "N/A"
        current_department = area.LookupParameter("Area Department").AsString()
        markdown = "skipping area {} becasue it is in group [**{}**]. Name = **{}**, Level = **{}**, Current Department = **{}**, Target Department = **{}**".format(output.linkify(area.Id),revit.doc.GetElement(area.GroupId).Name, area_name, area.Level.Name, current_department, department)
        output.print_md(markdown)
        in_group_area_found = True
        return
    try:
        area.LookupParameter("Area Department").Set(department)
    except Exception as e:
        print("*"*10)
        print("skipping area {} ".format(output.linkify(area.Id)))
        print (e)
        print("*"*10)

def try_to_fix_area(department):

    #global area_department_checklist
    fix_options = list(area_department_checklist)
    fix_options.insert(0,"<skip tartget, do it later...>")

    target = forms.SelectFromList.show(button_name = "pick a target department", \
                                        context = fix_options, \
                                        multiselect = False,\
                                        title = "[{}]--->?".format(department))

    if target == fix_options[0]:
        return
    similar_areas = filter(lambda x: x.LookupParameter("Area Department").AsString() == department, get_all_areas())
    map(lambda x: set_area_department(x, target), similar_areas)





def pick_bad_department():
    bad_areas = filter(lambda x: not is_department_in_checklist(x), get_all_areas())

    bad_areas = list({x.LookupParameter("Area Department").AsString() for x in bad_areas})
    bad_areas.sort(reverse = True)
    bad_areas.insert(0,"<select me to finish tool>")

    return forms.SelectFromList.show(button_name = "pick a department to fix", \
                                        context = bad_areas, \
                                        multiselect = False,\
                                        title = "i have found those department names not exist in master color pallte")

################## main code below #####################
output = script.get_output()
output.close_others()
in_group_area_found = False

area_department_checklist = ["OFFICE",\
                            "OTHERS",\
                            "PUBLIC CIRCULATION",\
                            "RETAIL",\
                            "SUPPORT",\
                            "VISITOR CENTER",\
                            "BASEMENT MEP & BOH"]






with revit.Transaction("fix area"):

    safety = 0

    while True:
        res = pick_bad_department()
        if res == "<select me to finish tool>":
            break
        if safety > 100:
            break
        safety += 1

        try_to_fix_area(res)


if in_group_area_found:
    forms.alert("some area cannot be changed becasue they are in a group. See output window for detail")
    output.show()
    output.set_width(1500)
    output.center()
