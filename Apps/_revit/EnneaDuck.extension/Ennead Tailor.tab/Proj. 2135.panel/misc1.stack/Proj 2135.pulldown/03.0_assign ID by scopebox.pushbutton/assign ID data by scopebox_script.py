__doc__ = "xxx"
__title__ = "03.0_Assign Bldg ID data\n by Scopebox"

from pyrevit import forms, DB, revit, script
import EA_UTILITY
import EnneadTab

def is_root_family(element):
    if element.SuperComponent  == None:
        return True
    return False

def fix_basement_ID():
    with revit.Transaction("Fix basement ID"):
        areas = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
        rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
        floors = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
        walls = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
        for element in list(areas) + list(rooms) + list(floors):
            level_name = revit.doc.GetElement( element.LevelId).Name
            if "SITE" in level_name: # and level_name != "SITE - LEVEL 1":
                element.LookupParameter("MC_$BuildingID").Set("SITE")



def check_associated_level(element):

    try:
        if not is_root_family(element):
            return False
    except:
        pass
    level_name = revit.doc.GetElement( element.LevelId).Name
    bldg_id = element.LookupParameter("MC_$BuildingID").AsString()

    """
    print(level_name)
    print(bldg_id)
    """


    def mark_bad(element):
        element.LookupParameter("Spatial Element Note").Set("Bad")

    element.LookupParameter("Spatial Element Note").Set("")
    if bldg_id == None :
        print("bad {} element, level = {}, but does not have bldging ID, the scopebox and element are not intersecting----{}".format(element.Category.Name, level_name, output.linkify(element.Id, title = "Go To Element")))
        mark_bad(element)
        return True
    if bldg_id not in level_name :
        print("bad {} element, level = {}, but building ID = {}, the element is location within the scopebox but associated wrong level.----{}".format(element.Category.Name, level_name, bldg_id, output.linkify(element.Id, title = "Go To Element")))
        try:
            print("element above is in [{}] area scheme".format(element.AreaScheme.Name))
        except:
            pass
        mark_bad(element)
        return True
    return False


def get_element_check_pt(element):
    if element is None:
        return None
    if hasattr(element, "Location"):
        if hasattr(element.Location, "Point"):
            return element.Location.Point
        if hasattr(element.Location, "Curve"):
            end0 = element.Location.Curve.GetEndPoint(0)
            end1 = element.Location.Curve.GetEndPoint(1)
            return DB.XYZ((end0.X + end1.X) * 0.5,
                            (end0.Y + end1.Y) * 0.5,
                            (end0.Z + end1.Z) * 0.5)

    # print element
    geo = element.Geometry[DB.Options()]

    b_box = geo.GetBoundingBox()
    min_pt = b_box.Min
    max_pt = b_box.Max
    return DB.XYZ((min_pt.X + max_pt.X) * 0.5,
                    (min_pt.Y + max_pt.Y) * 0.5,
                    (min_pt.Z + max_pt.Z) * 0.5)

def is_element_inside_scopebox(element, scopebox):
    #print element.Location.Point
    scope_geo = scopebox.Geometry[DB.Options()].GetBoundingBox()
    min_pt = scope_geo.Min
    max_pt = scope_geo.Max
    outline = DB.Outline(min_pt, max_pt)

    check_pt = get_element_check_pt(element)

    try:
        if outline.Contains(check_pt, 0):
            return True
    except:
        print("skipping element: [{}]{} becasue cannot find a location.".format(element.Category.Name, output.linkify(element.Id)))

    return False
"""
    try:
        if outline.Contains(element.Location.Point, 0):
            return True
    except:
        try:
            if outline.Contains(element.Location.Curve.GetEndPoint(0), 0):
                return True
        except:
            print("skipping element: {} becasue cannot find a location, possiblly a not placed area or room".format(output.linkify(element.Id)))

    return False
"""


def category_to_element(category, scopebox):
    bic = DB.BuiltInCategory.Parse(DB.BuiltInCategory,category)
    all_elements_raw = DB.FilteredElementCollector(revit.doc).OfCategory(bic).WhereElementIsNotElementType().ToElements()
    if category in ["Rooms", "Areas"]:
        all_elements = filter(lambda x: x.Area > 0, all_elements_raw)
    else:
        all_elements = all_elements_raw
    return filter(lambda x: is_element_inside_scopebox(x, scopebox), all_elements)




################## main code below #####################
output = script.get_output()
output.close_others()



#pick to process parameter " Plot ID" or "Building ID" or user define
#ID_para = forms.SelectFromList.show(["MC_$PlotID", "MC_$BuildingID","<As you type in>"], title='Select parameter you want to push data into.', multiselect = False)
ID_para = "MC_$BuildingID"


if ID_para == "<As you type in>":
    ID_para = forms.ask_for_string(prompt="Type below the parameter name used to get parameter", title = "get parameter")

if ID_para == None:
    forms.alert("None selected, cancelling action.")
    script.exit()


#pick scopebox to search
all_scopeboxs = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_VolumeOfInterest).WhereElementIsNotElementType().ToElements()
temp_options = sorted(list(all_scopeboxs), key = lambda x: x.Name)
#temp_options.sort(key = lambda x: x, reverse = False)

scopeboxs = forms.SelectFromList.show(temp_options, name_attr = "Name", multiselect = True, title = "search inside this scopebox")

#type in target data
#target_id = forms.ask_for_string(default = scopebox.Name, prompt="Target parameter Name = {0}\n\nType below the target ID for {0}".format(ID_para), title="where to ?")
#target_ids = [scopebox.Name for scopebox in scopeboxs]
#print target_id


#pick to assign categary: room, area, floor, wall, view, sheet, column, grid, ceiling   ["Rooms",\

#"Rooms",\
category = forms.SelectFromList.show(["Areas",\
                                    "Furniture",\
                                    "Rooms",
                                    "Floors",
                                    "Walls"],
                                    title='Select category you want to push data into.', multiselect = True)
#category = "Areas"

if len(category) == 0:
    forms.alert("None selected, cancelling action.")
    script.exit()
for i in range(len(category)):
    category[i] = "OST_" + category[i]




#find room area location in scopebox


#if have this parameter then change
def process_within_scopebox(scopebox):
    global category
    target_id = scopebox.Name
    print("   .")
    print("[Working on scopebox: {}]".format(target_id))
    with revit.Transaction("Push ID data"):
        for cate in category:
            print("*"*20)
            current_elements = category_to_element(cate, scopebox)
            print("---processing {}, {} elements found".format(cate, len(current_elements)))
            if len(current_elements) == 0:
                continue
            if current_elements[0].LookupParameter(ID_para) == None:
                print("This category have no parameter {}".format(ID_para))
                continue

            for element in current_elements:
                """
                print(element.Name)
                print(ID_para)
                print(element.LookupParameter(ID_para).AsString())
                """
                if EA_UTILITY.is_owned(element):
                    print("skipping {} due to ownership.")
                    continue
                try:
                    element.LookupParameter(ID_para).Set(target_id)
                except Exception as e:
                    print(element.Id)
                    try:
                        print("skipping {}, {}".format(element.Name, e))
                    except:
                        print("skipping {}, {}".format(element.LookupParameter("Name").AsString(), e))

with revit.TransactionGroup("Push ID data by scopebox"):
    map(process_within_scopebox, scopeboxs)
    fix_basement_ID()

print("all elements processed.")

t = DB.Transaction(revit.doc, "mark bad")
t.Start()
output.freeze()
for cate in category:
    bic = DB.BuiltInCategory.Parse(DB.BuiltInCategory,cate)
    all_elements_raw = DB.FilteredElementCollector(revit.doc).OfCategory(bic).WhereElementIsNotElementType().ToElements()
    if cate in ["Rooms", "Areas"]:
        all_elements = filter(lambda x: x.Location != None and x.Area > 0, all_elements_raw)
    else:
        all_elements = all_elements_raw

    bad = filter(check_associated_level, all_elements)
    if len(bad) > 0:
        print("*" * 20)
        forms.alert("{} have {} bad placement, check output window for detail".format(cate, len(bad)))
output.unfreeze()
output.set_width(1200)
t.Commit()
