#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "For many cateogries, set or recover the color and surface pattern status so the dwg can have non-solid hatch. Many LDI prefer the dwg this way, while EA pdf would prefer to show full foreground and background surface pattern."
__title__ = "44_set/recover no color elevation/sections/plans"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def get_category_by_name(parent_name, sub_c_name):
    all_categories = doc.Settings.Categories
    for category in all_categories:
        if category.Name != parent_name:
            continue
        if sub_c_name == None:
            return category
        for sub_c in category.SubCategories:
            if sub_c.Name == sub_c_name:
                #print sub_c
                return sub_c
    print("cannot find {}:{}".format(parent_name, sub_c_name))
    return None

def set_cate_cut_pattern(template, CATE, is_no_color_fill):
    # do it twice, once to modify cut foreground, once to modify cut background
    set_cate_pattern_hidden_status(template, CATE, is_no_color_fill, modify_surface = False, modify_foreground = True)
    set_cate_pattern_hidden_status(template, CATE, is_no_color_fill, modify_surface = False, modify_foreground = False)

def set_cate_surface_pattern(template, CATE, is_no_color_fill):
    # do it twice, once to modify surface foreground, once to modify surface background
    set_cate_pattern_hidden_status(template, CATE, is_no_color_fill, modify_surface = True, modify_foreground = True)
    set_cate_pattern_hidden_status(template, CATE, is_no_color_fill, modify_surface = True, modify_foreground = False)

def set_cate_pattern_hidden_status(template, cate, to_be_hidden, modify_surface = True, modify_foreground = True):
    if cate is None:
        return

    override_setting = template.GetCategoryOverrides(cate.Id)
    if modify_surface:
        if modify_foreground:
            override_setting.SetSurfaceForegroundPatternVisible(not(to_be_hidden))
            print("[{}] surface foreground pattern--->{}".format(cate.Name, "hidden" if to_be_hidden else "shown"))
        else:
            override_setting.SetSurfaceBackgroundPatternVisible(not(to_be_hidden))
            print("[{}] surface background pattern--->{}".format(cate.Name, "hidden" if to_be_hidden else "shown"))
    else:
        if modify_foreground:
            override_setting.SetCutForegroundPatternVisible(not(to_be_hidden))
            print("[{}] cut foreground pattern--->{}".format(cate.Name, "hidden" if to_be_hidden else "shown"))
        else:
            override_setting.SetCutBackgroundPatternVisible(not(to_be_hidden))
            print("[{}] cut foreground pattern--->{}".format(cate.Name, "hidden" if to_be_hidden else "shown"))


    try:
        template.SetCategoryOverrides (cate.Id, override_setting)

    except Exception as e:
        print("{} failed".format(cate.Name))

def set_cate_hidden_status(template, cate, to_be_hidden):
    #cat_id = DB.ElementId(int(cat_id))
    if cate is None:
        return
    try:
        template.SetCategoryHidden (cate.Id, to_be_hidden)
        print("[{}]--->{}".format(cate.Name, "hidden" if to_be_hidden else "shown"))
    except Exception as e:
        print("{} failed".format(cate.Name))


def set_filter_surface_pattern_hidden_status(template, filter, to_be_hidden, use_foreground = True, use_background = False):
    """
    for rooms in refugee area, rooms in elevator shaft, we need to keep color. The definition is controled in project UI.
    Here we are just to modify the surface display of those room to be no show or not.
    """
    filter_override_setting = DB.OverrideGraphicSettings()
    if use_foreground:
        filter_override_setting.SetSurfaceForegroundPatternVisible(not(to_be_hidden))

    if use_background:
        filter_override_setting.SetSurfaceBackgroundPatternVisible(not(to_be_hidden))

    template.SetFilterOverrides (filter.Id, filter_override_setting)


def set_filter_surface_pattern_as_grey(template, filter, to_be_hidden):
    filter_override_setting = DB.OverrideGraphicSettings()
    if to_be_hidden:
        grey_color = DB.Color(220,220,220)
        filter_override_setting.SetSurfaceBackgroundPatternColor(grey_color)
    template.SetFilterOverrides (filter.Id, filter_override_setting)

def get_filter_by_name(name):
    #Room_Elevator Shaft
    #Room_Refuge

    #get the filter for id of the rooms mentioned in funcs description above
    view_filters = DB.FilteredElementCollector(doc).OfClass(DB.FilterElement).WhereElementIsNotElementType().ToElements()
    try:
        return filter(lambda x: x.Name == name, view_filters)[0]
    except Exception as e:
        print("cannot find filter:<" + name + ">")
        print (e)
        return None





def modify_template_for_PDF(template, is_no_color_fill):
    print("--------------")
    template_name = template.Name
    print("modifying template [{}]".format(template_name))
    is_elevation = "elevation" in template_name.lower()
    is_section = "section" in template_name.lower()
    is_plan = "plan" in template_name.lower()
    is_axon = "axon" in template_name.lower()
    """
    if all([is_elevation, is_section, is_plan, is_axon]) == False:
        print("Cannot find keyword in this template")
    """
    # get following category id to turn off/on: FRW_H, FRW_V, room color
    # get following category id to enable/disable pattern display in surface: Detail item, curtain panel, generic model
    CATE_FRW_H = get_category_by_name("Generic Models", "FRW_shape_H")
    CATE_FRW_V = get_category_by_name("Generic Models", "FRW_shape_V")
    CATE_room_color = get_category_by_name("Rooms", "Color Fill")
    CATE_detail_items = get_category_by_name("Detail Items", None)
    CATE_curtain_panels = get_category_by_name("Curtain Panels", None)
    CATE_generic_models = get_category_by_name("Generic Models", None)
    CATE_floors = get_category_by_name("Floors", None)
    CATE_walls = get_category_by_name("Walls", None)
    CATE_doors = get_category_by_name("Doors", None)
    CATE_roofs = get_category_by_name("Roofs", None)
    CATE_windows = get_category_by_name("Windows", None)
    CATE_columns = get_category_by_name("Columns", None)
    CATE_structural_columns = get_category_by_name("Structural Columns", None)
    CATE_callouts = get_category_by_name("Callouts", None)
    CATE_room_seperation_lines = get_category_by_name("Lines", "<Room Separation>")



    #forever off:
    CATE_curtain_panels_ID = get_category_by_name("Curtain Panels", "ID")
    CATE_generic_models_ID = get_category_by_name("Generic Models", "ID")
    set_cate_hidden_status(template, CATE_curtain_panels_ID, True)
    set_cate_hidden_status(template, CATE_generic_models_ID, True)
    set_cate_hidden_status(template, CATE_callouts, True)
    set_cate_hidden_status(template, CATE_room_seperation_lines, True)
    markup_dim_filter = get_filter_by_name("dim_internal")
    if markup_dim_filter is not None:
        template.SetFilterVisibility (markup_dim_filter.Id, False)


    #  for elevations:
    if is_elevation or is_axon:
        print("use elevation axon rule")
        # always on: FRW_H, FRW_V
        set_cate_hidden_status(template, CATE_FRW_H, True)
        set_cate_hidden_status(template, CATE_FRW_V, False)


        # enable/disable pattern display in surface: Detail item,
        set_cate_surface_pattern(template, CATE_detail_items, is_no_color_fill)


        # always on pattern display in surface: generic model
        set_cate_surface_pattern(template, CATE_generic_models, False)


        # enable/disable pattern display in background surface: floor
        set_cate_pattern_hidden_status(template, CATE_floors, is_no_color_fill, modify_surface = True, modify_foreground = False)


        #door, windows will keep color on

        set_cate_pattern_hidden_status(template, CATE_doors, False, modify_surface = True, modify_foreground = False)
        set_cate_pattern_hidden_status(template, CATE_windows, False, modify_surface = True, modify_foreground = False)

        #curtain panel show all surface pattern
        set_cate_surface_pattern(template, CATE_curtain_panels, False)

    #  for sections:
    if is_section:
        print("use section rule")
        # always on: FRW_H, FRW_V, room color
        set_cate_hidden_status(template, CATE_FRW_H, True)
        set_cate_hidden_status(template, CATE_FRW_V, False)

        # turn off/on:  room color
        set_cate_hidden_status(template, CATE_room_color, is_no_color_fill)

        # enable/disable pattern display in surface:  generic model
        set_cate_surface_pattern(template, CATE_generic_models, is_no_color_fill)


        # make sure detail item color category is alwasy on, BUT set other special detail item to preserver color.
        set_cate_surface_pattern(template, CATE_detail_items, False)
        preserved_color_filter = get_filter_by_name("Detail Item_all but preserved color")
        if preserved_color_filter is not None:
            set_filter_surface_pattern_hidden_status(template, preserved_color_filter, is_no_color_fill)


        # enable/disable pattern display in background surface: floor
        set_cate_pattern_hidden_status(template, CATE_floors, is_no_color_fill, modify_surface = True, modify_foreground = False)


        # enable/disable pattern display in cut: curtain panel, generic model, wall
        set_cate_cut_pattern(template, CATE_curtain_panels, is_no_color_fill)
        set_cate_cut_pattern(template, CATE_generic_models, is_no_color_fill)
        set_cate_cut_pattern(template, CATE_walls, is_no_color_fill)

        # always on cut pattern: floor
        set_cate_cut_pattern(template, CATE_floors, False)

    #  for plans:
    if is_plan:
        print("use plan rule")
        # always on: FRW_H, FRW_V
        set_cate_hidden_status(template, CATE_FRW_H, False)
        set_cate_hidden_status(template, CATE_FRW_V, True)

        # make sure detail item color category is alwasy on, BUT set other special detail item to preserver color.
        set_cate_surface_pattern(template, CATE_detail_items, False)
        preserved_color_filter = get_filter_by_name("Detail Item_all but preserved color")
        if preserved_color_filter is not None:
            set_filter_surface_pattern_hidden_status(template, preserved_color_filter, is_no_color_fill, use_foreground = True,  use_background = True)

        # make sure room color category is alwasy on, BUT set other special room to preserver color.
        set_cate_hidden_status(template, CATE_room_color, False)
        preserved_color_filter = get_filter_by_name("Room_all but preserved color")
        if preserved_color_filter is not None:
            set_filter_surface_pattern_hidden_status(template, preserved_color_filter, is_no_color_fill)


        # make sure generic category  is alwasy on, BUT set other generic model  to preserver color.
        set_cate_surface_pattern(template, CATE_generic_models, False)
        preserved_color_filter = get_filter_by_name("Generic Model_all but preserved color")
        if preserved_color_filter is not None:
            set_filter_surface_pattern_hidden_status(template, preserved_color_filter, is_no_color_fill)
        preserved_color_filter = get_filter_by_name("Generic Model_preserved color")
        if preserved_color_filter is not None:
            set_filter_surface_pattern_as_grey(template, preserved_color_filter, is_no_color_fill)

        # enable/disable pattern display in surface: , roof
        set_cate_surface_pattern(template, CATE_roofs, is_no_color_fill)

        # enable/disable pattern display in background surface: ,floor
        set_cate_pattern_hidden_status(template, CATE_floors, is_no_color_fill, modify_surface = True, modify_foreground = False)




        # enable/disable pattern display in cut: generic model,
        set_cate_cut_pattern(template, CATE_generic_models, is_no_color_fill)

        # enable/disable pattern display in cut: curtain panel,
        set_cate_pattern_hidden_status(template, CATE_curtain_panels, is_no_color_fill, modify_surface = False, modify_foreground = False)
        set_cate_pattern_hidden_status(template, CATE_curtain_panels, False, modify_surface = False, modify_foreground = True)
        # enable/disable background surface pattern display in project, foreground always true: curtain panel,
        set_cate_pattern_hidden_status(template, CATE_curtain_panels, is_no_color_fill, modify_surface = True, modify_foreground = False)
        set_cate_pattern_hidden_status(template, CATE_curtain_panels, False, modify_surface = True, modify_foreground = True)

        # always one:wall
        set_cate_cut_pattern(template, CATE_walls, False)

        #make sure , column, structural column, category is always on
        set_cate_cut_pattern(template, CATE_columns, False)
        set_cate_cut_pattern(template, CATE_structural_columns, False)


    pass


def modify_template_for_DWG(template, is_no_color_fill):
    print("--------------")
    template_name = template.Name
    print("modifying template [{}]".format(template_name))
    is_elevation = "elevation" in template_name.lower()
    is_section = "section" in template_name.lower()
    is_plan = "plan" in template_name.lower()
    is_axon = "axon" in template_name.lower()
    """
    if all([is_elevation, is_section, is_plan, is_axon]) == False:
        print("Cannot find keyword in this template")
    """
    # get following category id to turn off/on: FRW_H, FRW_V, room color
    # get following category id to enable/disable pattern display in surface: Detail item, curtain panel, generic model
    CATE_FRW_H = get_category_by_name("Generic Models", "FRW_shape_H")
    CATE_FRW_V = get_category_by_name("Generic Models", "FRW_shape_V")
    CATE_room_color = get_category_by_name("Rooms", "Color Fill")
    CATE_detail_items = get_category_by_name("Detail Items", None)
    CATE_curtain_panels = get_category_by_name("Curtain Panels", None)
    CATE_generic_models = get_category_by_name("Generic Models", None)
    CATE_floors = get_category_by_name("Floors", None)
    CATE_walls = get_category_by_name("Walls", None)
    CATE_doors = get_category_by_name("Doors", None)
    CATE_roofs = get_category_by_name("Roofs", None)
    CATE_windows = get_category_by_name("Windows", None)
    CATE_columns = get_category_by_name("Columns", None)
    CATE_structural_columns = get_category_by_name("Structural Columns", None)
    CATE_callouts = get_category_by_name("Callouts", None)



    #forever off:
    CATE_curtain_panels_ID = get_category_by_name("Curtain Panels", "ID")
    CATE_generic_models_ID = get_category_by_name("Generic Models", "ID")
    set_cate_hidden_status(template, CATE_curtain_panels_ID, True)
    set_cate_hidden_status(template, CATE_generic_models_ID, True)
    set_cate_hidden_status(template, CATE_callouts, True)


    #  for elevations:
    if is_elevation or is_axon:
        print("use elevation axon rule")
        # always on: FRW_H, FRW_V
        set_cate_hidden_status(template, CATE_FRW_H, True)
        set_cate_hidden_status(template, CATE_FRW_V, False)

        # enable/disable pattern display in surface: Detail item, generic model
        set_cate_surface_pattern(template, CATE_detail_items, is_no_color_fill)
        set_cate_surface_pattern(template, CATE_generic_models, is_no_color_fill)


        # enable/disable pattern display in background surface: floor
        set_cate_pattern_hidden_status(template, CATE_floors, is_no_color_fill, modify_surface = True, modify_foreground = False)


        #enable/disable pattern display in background surface: curtain panel, door, windows
        set_cate_pattern_hidden_status(template, CATE_curtain_panels, is_no_color_fill, modify_surface = True, modify_foreground = False)
        set_cate_pattern_hidden_status(template, CATE_doors, is_no_color_fill, modify_surface = True, modify_foreground = False)
        set_cate_pattern_hidden_status(template, CATE_windows, is_no_color_fill, modify_surface = True, modify_foreground = False)


    #  for sections:
    if is_section:
        print("use section rule")
        # always on: FRW_H, FRW_V, room color
        set_cate_hidden_status(template, CATE_FRW_H, True)
        set_cate_hidden_status(template, CATE_FRW_V, False)

        # turn off/on:  room color
        set_cate_hidden_status(template, CATE_room_color, is_no_color_fill)

        # enable/disable pattern display in surface:  generic model,detail item
        set_cate_surface_pattern(template, CATE_generic_models, is_no_color_fill)
        set_cate_hidden_status(template, CATE_detail_items, is_no_color_fill)


        # enable/disable pattern display in background surface: floor
        set_cate_pattern_hidden_status(template, CATE_floors, is_no_color_fill, modify_surface = True, modify_foreground = False)


        # enable/disable pattern display in cut: curtain panel, generic model, wall, floor
        set_cate_cut_pattern(template, CATE_curtain_panels, is_no_color_fill)
        set_cate_cut_pattern(template, CATE_generic_models, is_no_color_fill)
        set_cate_cut_pattern(template, CATE_walls, is_no_color_fill)
        set_cate_cut_pattern(template, CATE_floors, is_no_color_fill)

    #  for plans:
    if is_plan:
        print("use plan rule")

        # always on: FRW_H, FRW_V
        set_cate_hidden_status(template, CATE_FRW_H, False)
        set_cate_hidden_status(template, CATE_FRW_V, True)

        # enable/disable room color category
        set_cate_hidden_status(template, CATE_room_color, is_no_color_fill)


        # enable/disable pattern display in surface:  generic model, roof
        set_cate_surface_pattern(template, CATE_generic_models, is_no_color_fill)
        set_cate_surface_pattern(template, CATE_roofs, is_no_color_fill)

        # enable/disable pattern display in background surface: Detail item,floor
        set_cate_pattern_hidden_status(template, CATE_floors, is_no_color_fill, modify_surface = True, modify_foreground = False)
        set_cate_pattern_hidden_status(template, CATE_detail_items, is_no_color_fill, modify_surface = True, modify_foreground = False)



        # enable/disable pattern display in cut: curtain panel, generic model, wall, column, structural column
        set_cate_cut_pattern(template, CATE_curtain_panels, is_no_color_fill)
        set_cate_cut_pattern(template, CATE_generic_models, is_no_color_fill)
        set_cate_cut_pattern(template, CATE_walls, is_no_color_fill)
        set_cate_cut_pattern(template, CATE_columns, is_no_color_fill)
        set_cate_cut_pattern(template, CATE_structural_columns, is_no_color_fill)


    pass

def redefine_selection_set(set_name):
    all_filters = DB.FilteredElementCollector(doc).OfClass(DB.FilterElement).ToElements()
    for filter in all_filters:
        if filter.Name == set_name:
            #filter.Clear()
            break
    else:
        filter = DB.SelectionFilterElement.Create(doc, set_name)
    return filter

def add_markup_dims_to_set(selection_set):
    all_dims = DB.FilteredElementCollector(doc).OfClass(DB.Dimension).WhereElementIsNotElementType().ToElements()
    markup_dims = filter(lambda x: x.DimensionType.LookupParameter("Type Name").AsString().lower() in ["markup", "sketch"], all_dims)
    selection_set.SetElementIds(EA_UTILITY.list_to_system_list([x.Id for x in markup_dims]))
################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:

#EA_UTILITY.dialogue(main_text = "At the moment, i have only setup the behavior map for plan templates. So it only set/recover plan template color.\n\nThis tool will be expanded to add behavior map for section and elevation template next week.")
# do i want to set/recover
options = ["Set No Color Fill", "Recover Color Fill"]
is_no_color_fill = EA_UTILITY.dialogue(options = options,
                                        main_text = "I want to [...] to view templates",
                                        sub_text = "Dean wants to keep glass color instead of true blank. So we can set 'Print_In_Color' checkerbox and print elevations in greyscale from bili printer.")

format_is_pdf = True
options = ["PDF(for Dean)", "DWG(for LDI)"]
res = EA_UTILITY.dialogue(options = options,
                        main_text = "Note:\nFor PDF and DWG export, we will need to run this tool seperately for each run. What Dean wants and what LDI wants cannot be achievd in one version of template.\n\nWhich format are you exporting now?")
if res == options[1]:
    format_is_pdf = False

# get templates to modify
selected_templates = forms.select_viewtemplates()
if selected_templates is None:
    script.exit()


# modify each template
t = DB.Transaction(doc, is_no_color_fill)
t.Start()

selection_set = redefine_selection_set("dim_internal")
add_markup_dims_to_set(selection_set)


is_no_color_fill = True if "No" in is_no_color_fill else False
if format_is_pdf:
    map(lambda x:modify_template_for_PDF(x, is_no_color_fill), selected_templates)
else:
    map(lambda x:modify_template_for_DWG(x, is_no_color_fill), selected_templates)
t.Commit()
print("tool finish")
