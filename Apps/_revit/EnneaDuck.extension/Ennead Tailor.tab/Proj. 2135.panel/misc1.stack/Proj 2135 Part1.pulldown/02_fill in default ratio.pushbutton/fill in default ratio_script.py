OTHERS__doc__ = "If the default discount ratio info has not been filled in, attempt to fill as 1.0"
__title__ = "02_fill in default discount ratio if has not been filled"

from pyrevit import forms, DB, revit, script




def check_area_content(area, fix = False):
    #check discount ration, and if not department infor presented
    #print str((area.LookupParameter("MC_$Discount Ratio").AsDouble() ))
    #print area.LookupParameter("MC_$Discount Ratio").HasValue
    if not area.LookupParameter("MC_$Discount Ratio").HasValue:
        if not fix:
            return False
        main_msg = "Level : Area Department : Name\n\n{} : [{}] : {} \n\ndoes not have a discount ratio value, do you want to give it as  [.....]".format(revit.doc.GetElement(area.LevelId).Name, area.LookupParameter("Area Department").AsString(),area.LookupParameter("Name").AsString())
        #print main_msg
        ratio_values = ["0","0.5","1"]
        ratio = float(forms.alert(options = ratio_values , msg = main_msg))
        area.LookupParameter("MC_$Discount Ratio").Set(ratio)
    #ask to fix? show detail information
    return True




def get_all_areas_in_GFA_scheme(doc = revit.doc):
    all_areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.AreaScheme.Name == "Gross Building", all_areas)


def print_area_detail(area):
    print("area detail: {};{}:{}--{}".format(area.Level.Name, area.LookupParameter("Area Department").AsString(), area.LookupParameter("Name").AsString(), EA_UTILITY.sqft_to_sqm(area.Area * area.LookupParameter("MC_$Discount Ratio").AsDouble())))


################## main code below #####################
output = script.get_output()
output.close_others()

check = filter(lambda x: not check_area_content(x, fix = False), get_all_areas_in_GFA_scheme())
if len(check) != 0:
    res = forms.alert(options = ["Fix Now", "Ignore"], msg = "There are {} area that has no discount ratio value assigned, i want to [...]".format(len(check)))
    if res == "Fix Now":
        with revit.Transaction("Fix up area number"):
            map(lambda x: check_area_content(x, fix = True), get_all_areas_in_GFA_scheme())
else:
    forms.alert("every area in Gross Building Area Scheme has a discount ratio value")
