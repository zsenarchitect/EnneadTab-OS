#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Batch create walltype filters with defined color to many view templates. \n\nThis is handy when doing the colored wall type diagram elevation."
__title__ = "52_Assign Walltype Filter"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def get_description(raw_name):
    return raw_name.split("]")[1].split("<")[0]

def get_color(raw_name):
    return raw_name.split("(")[1].split(")")[0].split(",")

def get_keynote(raw_name):
    return raw_name.split("<")[1].split(">")[0]

def create_filter_by_name(name):
    filter = DB.ParameterFilterElement.Create(doc, name, EA_UTILITY.list_to_system_list([DB.ElementId (DB.BuiltInCategory.OST_Walls)]) )
    #rule_list = []
    return filter.Id

    sample_wall_element = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().FirstElement()
    paramId = sample_wall_element.LookupParameter("Type Name").Id
    # create a "not ends with" filter rule
    check = name.split("WallType_")[1]
    eq_rule = DB.ParameterFilterRuleFactory.CreateEqualsRule (paramId, check, False)
    # create parameter filter element
    #paramFilterElem = ParameterFilterElement.Create(doc, ifilter,CateIds,[eq_rule])
    filter = DB.ParameterFilterElement.Create(doc, name, EA_UTILITY.list_to_system_list([DB.ElementId (DB.BuiltInCategory.OST_Walls)]), [eq_rule] )
    filter.SetElementFilter (eq_rule)
    """
    # set filter overrides (same with add filter to current)
    active_view.SetFilterOverrides(paramFilterElem.Id, OverrideGraphicSettings())
    """
    return filter.Id

def get_filter_id_by_name(raw_name):
    name = get_description(raw_name)
    #get the id of the office layout filter
    view_filters = DB.FilteredElementCollector(doc).OfClass(DB.FilterElement).WhereElementIsNotElementType().ToElements()

    for v in view_filters:
        if v.Name == name:
            return v.Id
    else:
        return create_filter_by_name(name)


def set_filter_graphic(template, filter_id, color):
    override_setting = DB.OverrideGraphicSettings()
    R, G, B = color

    override_setting.SetSurfaceForegroundPatternColor(DB.Color(int(R), int(G), int(B)))

    solid_fill_id = EnneadTab.REVIT.REVIT_SELECTION.get_solid_fill_pattern_id(doc)
    override_setting.SetSurfaceForegroundPatternId(solid_fill_id)
    try:
        template.SetFilterOverrides (filter_id, override_setting)
    except Exception as e:
        print "skip {} becasue:{}".format(template.Name, e)
################## main code below #####################
output = script.get_output()
output.close_others()

# format: [plot name]WallType_Facade Name(Red, Green, Blue)
desired_filters = ["[N3]WallType_Stone<石材 ST-1/1A>(255, 255, 255)",
                    "[N5N6]WallType_Stone<石材 ST-1>(255, 255, 255)",
                    "[N3N5N6]WallType_Storefront Facade<橱窗立面幕墙 SF-1>(238, 185, 123)",
                    "[N3N5N6]WallType_Railing<玻璃护栏 RLG-1>(220, 232, 200)",
                    "[N3]WallType_Tower Facade<主立面玻璃幕墙 CW-1>(121, 157, 193)",
                    "[N5N6]WallType_Bili Way Facade<主立面玻璃幕墙 CW-1>(121, 157, 193)",
                    "[N4]WallType_Folding Facade<CW-1>(121, 157, 193)",
                    "[N3]WallType_Tower Zipper Facade<内凹立面幕墙 CW-2>(208, 238, 255)",
                    "[N5N6]WallType_Reveal Facade<内凹立面幕墙 CW-2>(208, 238, 255)",
                    "[N4]WallType_Storefront Facade<CW-2>(208, 238, 255)",
                    "[N3N5]WallType_Glass Fin Wall Facade<玻璃肋幕墙 CW-3>(253, 248, 211)",
                    "[N4]WallType_Sunken Plaza Facade<CW-3>(253, 248, 211)",
                    "[N3]WallType_Generic Facade<通用玻璃幕墙 CW-4/4A>(141, 200, 200)",
                    "[N6]WallType_Connector Facade<连楼玻璃幕墙 CW-4>(141, 200, 200)",
                    "[N3N5N6]WallType_Bridge Facade<连桥立面 CW-4B>(224, 134, 117)",
                    "[N4]WallType_Sunken Plaza Recess Facade<CW-4>(141, 200, 200)",
                    "[N3]WallType_Podium Facade<裙楼玻璃幕墙 CW-5/5A>(125, 166, 145)",
                    "[N6]WallType_Bili Stage Facade<圆环舞台玻璃幕墙 CW-5>(125, 166, 145)",
                    "[N3]WallType_Sphere Facade Glass<球玻璃幕墙 CW-6>(255, 189, 228)",
                    "[N3]WallType_Sphere Facade Metal<球金属板幕墙 MP-4>(235, 151, 163)",
                    "[N3]WallType_Dome Facade<拱立面 ST-2/2A>(241, 215, 218)",
                    "[N6]WallType_Resi Facade<住宅窗墙 CW-6>(255, 189, 228)",
                    "[N3]WallType_Blockout Facade<遮挡立面幕墙 CW-7/7A>(178, 163, 144)",
                    "[N6]WallType_Village Facade<24m独栋玻璃幕墙 CW-7>(178, 163, 144)",
                    "[N3]WallType_Skylight<天光 SKY-1/2/3>(128, 255, 255)",
                    "[N4]WallType_Skylight Facade<SKY-1>(128, 255, 255)",
                    "[N3N5]WallType_Mushroom<蘑菇造型 MP-1A>(87, 162, 210)",
                    "[N5N6]WallType_LED Screen<屏幕 LED>(255, 202, 228)"]

if __name__ == "__main__":
    selected_filters = forms.SelectFromList.show(desired_filters,
                                                multiselect = True,
                                                title = "What walltype do you want? Search plot Id to narrow down.")

    if selected_filters is None:
        script.exit()

    all_templates = [v for v in DB.FilteredElementCollector(doc).OfClass(DB.View) if v.IsTemplate]
    selected_template = forms.SelectFromList.show(all_templates,
                                                multiselect = True,
                                                name_attr = "Name")
    if selected_template is None:
        script.exit()


    t = DB.Transaction(doc, "assign filter by creation")
    t.Start()
    for filter in selected_filters:
        print doc.GetElement(get_filter_id_by_name(filter)).Name

        for template in selected_template:
            color = get_color(filter)
            set_filter_graphic(template, get_filter_id_by_name(filter), color)

    t.Commit()
