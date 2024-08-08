__doc__ = "Legacy, now in review panel"
__title__ = "01_remove not placed area(Legacy)"

from pyrevit import forms, DB, revit, script
from EA_UTILITY import dialogue

################## main code below #####################
output = script.get_output()
output.close_others()

all_areas = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
with revit.Transaction("Delete Not Placed area"):
    count = 0
    nega_count = 0
    for area in all_areas:
        if area.Location == None and area.Area == 0:
            revit.doc.Delete(area.Id)
            continue
            count += 1

        if area.Area < 0:
            print("this area has negative area. Area Scheme = {}, Level = {}, area name = {}----{}".format(area.AreaScheme.Name,  revit.doc.GetElement(area.LevelId).Name,area.LookupParameter("Name").AsString(), output.linkify(area.Id, title = "Go To Area")))
            nega_count += 1

if count > 0:
    dialogue(main_text = "{} not placed areas are removed from project.".format(count))

if nega_count > 0:
    dialogue(main_text = "{} negative area in projects".format(nega_count))
print("*"*100)







all_rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
with revit.Transaction("Delete Not Placed rooms"):
    count = 0
    for room in all_rooms:
        if room.Location == None and room.Area == 0:
            revit.doc.Delete(room.Id)
            count += 1

if count > 0:
    dialogue(main_text = "{} not placed rooms are removed from project.".format(count))






all_rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
count = 0
open_rooms = []
for room in all_rooms:
    if room.Area == 0:
        count += 1
        open_rooms.append(room)
if count > 0:
    output.insert_divider()
    print("*"*100)

    dialogue(main_text = "{} not enclosed room or redundent room still in the project.".format(count), icon = "warning")
    for room in open_rooms:
        #print area.LookupParameter("Area").AsValueString() ### is this equal to redundent or not enclosed?
        #print area.Perimeter
        #print area.Geometry[DB.Options()]
        print("not enclosed room or redundent room.  Level = {}, room department = {}, room name = {}----{}".format( revit.doc.GetElement(room.LevelId).Name, room.LookupParameter("Department").AsString(),room.LookupParameter("Name").AsString(), output.linkify(room.Id, title = "Go To Room")))
else:
    dialogue(main_text = "no non-enclose or redundent Room found.")








all_areas = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
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
        print("not enclosed area or redundent area. Area Scheme = {}, Level = {}, area department = {}, area name = {}----{}".format(area.AreaScheme.Name, revit.doc.GetElement(area.LevelId).Name, area_department,area.LookupParameter("Name").AsString(), output.linkify(area.Id, title = "Go To Area")))
else:
    dialogue(main_text = "no non-enclose or redundent area found.")








output.insert_divider()
print("*"*100)

count = 0
for area in all_areas:
    if area.AreaScheme.Name != "Gross Building":
        continue
    if area.LookupParameter("Area Department").AsString() == None:

        print("this area has no area department assignemted to it. Area Scheme = {}, Level = {}, area name = {}----{}".format(area.AreaScheme.Name,  revit.doc.GetElement(area.LevelId).Name,area.LookupParameter("Name").AsString(), output.linkify(area.Id, title = "Go To Area")))
        count += 1
if count > 0:
    dialogue(main_text = "{} area has empty area department value in gross buiilding area scheme. See output window for detail".format(count), icon = "warning")
else:
    dialogue(main_text = "no empty area department value found")


output.set_width(1100)
output.set_height(800)
# output.center()
