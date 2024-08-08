__doc__ = "pick panel types to be fixed, it will update the 'R' or 'r' parameter based on the curved host wall"
__title__ = "10_By List: multiple panel radius by host wall"

from pyrevit import forms, DB, revit, script
import EA_UTILITY
import EnneadTab

def find_similar_panels(type_id):

    family_name = type_id.split("}:")[0].replace("{","")
    type_name = type_id.split("}:")[1]

    def is_match_panel(x):
        try:
            if family_name == x.Symbol.FamilyName and type_name == x.Symbol.LookupParameter("Type Name").AsString():
                return True
            else:
                return False
        except Exception as e:
            if "has no attribute" in str(e):
                return False
            else:
                print (e)
                print(x.Id)
                return False

    all_panels = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()
    panels = filter(lambda x: is_match_panel(x), all_panels)

    return panels

def find_panel_host_wall_radius(panel):

    radius = panel.Host.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_ARC_RADIUS).AsDouble()
    if radius == 0.0:
        print("Panel {} should be in curved wall.{}".format(panel.Id, output.linkify(panel.Id,title = "Click to zoom to panel")))
        global error_panel_found
        error_panel_found = True

    return radius

def types_not_in_list(list):
    panel_types = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsElementType().ToElements()
    OUT = []
    for panel_type in panel_types:
        family_name = panel_type.FamilyName
        type_name = panel_type.LookupParameter("Type Name").AsString()
        format_name = "{{{}}}:{}".format(family_name, type_name)
        if "arc" not in format_name.lower():
            continue
        if format_name not in list:
            OUT.append(format_name)

    if len(OUT) == 0:
        return None
    return OUT
################## main code below #####################
output = script.get_output()
output.close_others()

error_panel_found = False

opts = ["{Edge Railing_Edge_Main}:Arc",\
        "{Edge Railing_Railing_Main}:Arc",\
        "{WW1 - CWPL}:Typical",\
        "{WW1 - CWPL_test}:Typical",\
        "{Edge Solid_Edge_Main}:Arc",\
        "{Edge Solid_Edge_2.0 Arc_Main}:Arc",\
        "{Sunken Plaza Railing_Main}:Arc",\
        "{N5N6 Louver Panel_Main}:Arc",\
        "{Bili_Arc_Main}:Arc",\
        "{Podium_Arc_Main}:Typ",\
        "{Edge Railing_Edge_Main_600}:Arc",\
        "{Edge Railing_Edge_Main_1000 bottom}:Arc",\
        "{SF glass mullion panel_dbl H_Main}:Arc",\
        "{Upper Podium_Metal Panel_Main}:Arc",\
        "{Upper Podium_Glazing Main}:Arc",\
        "{N3 Canopy at Tower Roof_arc}:SD",\
        "{Blade Podium Round head_Arc Offset_Main}:SD",\
        "{Biliway 2.0_Arc_Main}:Arc",\
        "{Biliway Round head 2.0_Main_Arc}:SD",\
        "{Biliway 2.0_Arc_Top_Main}:Arc",\
        "{Blade Podium Round head_Main_Arc}:SD",\
        "{Blade Podium Round head_Arc_Main}:SD",\
        "{Blade Podium_Arc_Main}:SD",\
        "{Blade Podium_Solid Arc_Main}:SD",\
        "{Bulkhead_Arc_Main}:SD",\
        "{Bulkhead Solid_Arc_Main}:SD",\
        "{SF panel_sgl H_Main}:Arc",\
        "{SF cable panel_dbl H_Main}:Arc",\
        "{SF Solid_Main}:Arc",\
        "{Ring_Main}:Outter",\
        "{Ring_Main}:Inner",\
        "{Cable Railing_Railing_Main}:Arc",\
        "{SF cable panel_top reveal_Main}:Arc",\
        "{Edge Railing_Main}:Arc",\
        "{Generic Panel_Main}:Arc",\
        "{Generic Panel Village_Main}:Arc",\
        "{Storefront Panel_Main}:Arc",\
        "{N5N6 Storefront Panel_Main}:Arc",\
        "{Storefront Panel Resi_Main}:Arc",\
        "{Solid Stone_Main}:Arc",\
        "{Solid Stone_Main_2.0}:Arc",\
        "{Upper Podium_Main}:Arc",\
        "{SF Panel_Main}:Arc",\
        "{Resi Panel_Main}:Arc",\
        "{Edge Railing_Railing_Resi}:Arc",\
        "{Connection Panel_Main}:Arc",\
        "{Upper Podium_Glazing}:Arc",\
        "{Base Solid_Edge_Main}:Arc",\
        "{Village Coping Panel_Main}:Arc",\
        "{Generic Panel Village_Main}:Arc",\
        "{Blade Podium Round head_Main_Arc Offset}:SD",\
        "{SF Glass Fin Panel_dbl H_Main}:Arc",\
        "{Cage Railing_Main}:Arc",\
        "{Village Coping Panel_Main terrace}:Arc"]

missing_types = types_not_in_list(opts)
if missing_types:
    print("Following types not in the data set:")
    OUT = ""
    for x in missing_types:
        print(x)
        OUT += "\n" + x

    EA_UTILITY.dialogue(main_text = "Following types not in the data set:",
                        sub_text = OUT)


types = forms.SelectFromList.show(opts,
                                multiselect = True,
                                button_name='Select Panel Type')

panels = []
if not types:
    script.exit()
for type in types:
    panels.extend(find_similar_panels(type))

fix_count = 0
with revit.Transaction("Panel get host wall radius"):
    for panel in panels:
        try:
            desires_r = find_panel_host_wall_radius(panel)
            if panel.LookupParameter("R").AsDouble() != desires_r:
                panel.LookupParameter("R").Set(desires_r)
                fix_count += 1
        except:
            print("panel might has no 'R' parameter. Check the name list.")


revit.get_selection().set_to(panels)
forms.alert("{} panels found, {} updated".format(len(panels), fix_count))
if error_panel_found:
    print("###")
    forms.alert("Also find curved panel(s) on a flat wall, please take a look at the output window.")
