__doc__ = "Relocate the furnichure level of the selected elements by building ID"
__title__ = "03.2_change furnichure level by bldg id"

from pyrevit import forms, DB, revit, script

def is_root_family(element):
    if element.SuperComponent  == None:
        return True
    return False

def get_level_by_name(name):
    levels = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    """
    for level in levels:
        if level.Name == name:
            return level
    """
    return filter(lambda x: x.Name == name, levels)[0].Id
    #return id

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

    if bldg_id == None :
        print("bad {} element, level = {}, but does not have bldging ID, try assigning ID by scopebox----{}".format(element.Category.Name, level_name, output.linkify(element.Id, title = "Go To Element")))
        return True
    if bldg_id not in level_name :
        #print element.Parameter[DB.BuiltInParameter.FAMILY_LEVEL_PARAM].AsString()
        print("bad {} element, level = {}, but building ID = {}, the element is location within the id scopebox but associated wrong level. Try to fix now".format(element.Category.Name, level_name, bldg_id))

        try:
            new_level_name = bldg_id + " - " + level_name.split(" - ")[1]
            print("\tattemping new level name = {}".format(new_level_name))
            #element.LookupParameter("Level").Set(get_level_by_name(new_level_name))
            element.Parameter[DB.BuiltInParameter.FAMILY_LEVEL_PARAM].Set(get_level_by_name(new_level_name))
            print("\tfixing successful, new level is {}".format(new_level_name))
        except:
            print("\tfixing failed, cannot find a new level or there is a ownership conflict, please fix mannually or ask Sen for instruction.----{}".format(output.linkify(element.Id, title = "Go To Element")))
        return True
    return False

def is_element_inside_scopebox(element, scopebox):
    #print element.Location.Point
    scope_geo = scopebox.Geometry[DB.Options()].GetBoundingBox()
    min_pt = scope_geo.Min
    max_pt = scope_geo.Max
    outline = DB.Outline(min_pt, max_pt)
    try:
        if outline.Contains(element.Location.Point, 0):
            return True

    except:
        print("skipping element: {} becasue cannot find a location, possiblly a not placed area or room".format(element.Id))

    return False

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




category = "OST_Furniture"




with revit.Transaction("fix furnichure level"):
    output.freeze()
    bic = DB.BuiltInCategory.Parse(DB.BuiltInCategory,category)
    all_elements = DB.FilteredElementCollector(revit.doc).OfCategory(bic).WhereElementIsNotElementType().ToElements()
    bad = filter(check_associated_level, all_elements)

    if len(bad) > 0:
        forms.alert("{} have {} bad placement, check output window for detail.\nAlso run assign id by scopebox again if need to.".format(category, len(bad)))
    else:
        print("all furnichure level and bldg ID matching")
    output.unfreeze()
