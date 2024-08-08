__doc__ = "Get areas with department assignment outside predefined name list. And attempt to fix them."
__title__ = "17_fix color_area office layout function"

from pyrevit import forms, DB, revit, script

def reset_area_function_other_than_office():
    areas = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    target_areas = filter(lambda x: x.AreaScheme.Name == "Gross Building" and x.LookupParameter("Area Department").AsString() != "OFFICE", areas)
    for area in target_areas:
        area.LookupParameter("Area Layout Function").Set("")

def get_all_areas():
    areas = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.AreaScheme.Name == "Gross Building" and x.LookupParameter("Area Department").AsString() == "OFFICE", areas)

def is_office_layout_in_checklist(area):
    global area_layout_function_checklist
    if area.LookupParameter("Area Layout Function").AsString() in area_layout_function_checklist:
        return True
    return False


def set_area_layout_function(area, layout_function):
    global in_group_area_found
    if area.GroupId.IntegerValue  > 0:
        area_name = area.LookupParameter("Name").AsString()
        if len(area_name) == 0:
            area_name = "N/A"
        current_layout_function = area.LookupParameter("Area Layout Function").AsString()
        markdown = "skipping area {} becasue it is in group [**{}**]. Name = **{}**, Level = **{}**, Current Department = **{}**, Target Department = **{}**".format(output.linkify(area.Id),revit.doc.GetElement(area.GroupId).Name, area_name, area.Level.Name, current_layout_function, layout_function)
        output.print_md(markdown)
        in_group_area_found = True
        return
    try:
        area.LookupParameter("Area Layout Function").Set(layout_function)
    except Exception as e:
        print("*"*10)
        print("skipping area {} ".format(output.linkify(area.Id)))
        print (e)
        print("*"*10)

def try_to_fix_area(layout_function):

    global area_layout_function_checklist

    target = forms.SelectFromList.show(button_name = "pick a target layout function", \
                                        context = area_layout_function_checklist, \
                                        multiselect = False,\
                                        title = "[{}]--->?".format(layout_function))
    similar_areas = filter(lambda x: x.LookupParameter("Area Layout Function").AsString() == layout_function, get_all_areas())
    map(lambda x: set_area_layout_function(x, target), similar_areas)





def pick_bad_layout_function():
    bad_areas = filter(lambda x: not is_office_layout_in_checklist(x), get_all_areas())

    bad_areas = list({x.LookupParameter("Area Layout Function").AsString() for x in bad_areas})
    bad_areas.sort(reverse = True)
    bad_areas.insert(0,"<select me to finish tool>")

    return forms.SelectFromList.show(button_name = "pick a layout function to fix", \
                                        context = bad_areas, \
                                        multiselect = False,\
                                        title = "i have found those layout function names not exist in master color pallte")


def change_core_related_office_area_name():
    areas = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    target_areas = filter(lambda x: x.AreaScheme.Name == "Gross Building" and x.LookupParameter("Area Department").AsString() == "OFFICE", areas)
    for area in target_areas:
        if area.LookupParameter("Area Layout Function").AsString() == "CORE":
            area.LookupParameter("Name").Set("CORE")
################## main code below #####################
output = script.get_output()
output.close_others()
in_group_area_found = False

area_layout_function_checklist = ["CORE",\
                                "NET OFFICE",\
                                "OFFICE AMENITY",\
                                "OFFICE CIRCULATION",\
                                "OFFICE TERRACE"]






with revit.Transaction("fix area office layout"):
    reset_area_function_other_than_office()
    safety = 0

    while True:
        res = pick_bad_layout_function()
        if res == "<select me to finish tool>":
            break
        if safety > 100:
            break
        safety += 1

        try_to_fix_area(res)
    change_core_related_office_area_name()


if in_group_area_found:
    forms.alert("some area cannot be changed becasue they are in a group. See output window for detail")
    output.show()
    output.set_width(1500)
    output.center()
