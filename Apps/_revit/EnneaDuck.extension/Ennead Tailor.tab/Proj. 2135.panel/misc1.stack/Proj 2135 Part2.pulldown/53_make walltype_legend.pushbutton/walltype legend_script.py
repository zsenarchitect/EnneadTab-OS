#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Legacy, now do it in output panel"
__title__ = "53_Make walltype legend(Legacy)"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore



def create_region_type(fill_region_type_name, fill_region_color):
    sample_type = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).FirstElement()
    filledregion_type = sample_type.Duplicate(fill_region_type_name)
    filledregion_type.ForegroundPatternId = EnneadTab.REVIT.REVIT_SELECTION.get_solid_fill_pattern_id(doc)
    R, G, B = fill_region_color
    filledregion_type.ForegroundPatternColor = DB.Color(int(R), int(G), int(B))
    filledregion_type.LineWeight = 1
    filledregion_type.IsMasking = True
    return filledregion_type

def get_region_type_by_name(name):

    region_types = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).ToElements()

    for region_type in region_types:
        if region_type.LookupParameter("Type Name").AsString() == name:
            return region_type
    return None

def update_fill_region_type_color(fill_region_type_name, fill_region_color):
    region_type = get_region_type_by_name(fill_region_type_name)
    R, G, B = fill_region_color
    #print R, G, B
    region_type.ForegroundPatternColor = DB.Color(int(R), int(G), int(B))


def make_title(base_point, fr_type):
    tnote_typeid = doc.GetDefaultElementTypeId(DB.ElementTypeGroup.TextNoteType)
    type_name = fr_type.LookupParameter("Type Name").AsString()
    if type_name is None:
        type_name = ""
    title = type_name.replace("WallType_", "") + "  " + get_keynote_by_description(type_name)
    DB.TextNote.Create(doc,
                       doc.ActiveView.Id,
                       DB.XYZ(base_point.X + SQUARE_EDGE_LENGTH + GAP, base_point.Y + SQUARE_EDGE_LENGTH - GAP, base_point.Z),
                       title,
                       tnote_typeid
                      )


def make_filledregion_element(base_point, fr_type):
    cloop = DB.CurveLoop()
    cloop.Append(
        DB.Line.CreateBound(
            DB.XYZ(base_point.X, base_point.Y, base_point.Z),
            DB.XYZ(base_point.X + SQUARE_EDGE_LENGTH, base_point.Y, base_point.Z)
            )
    )
    cloop.Append(
        DB.Line.CreateBound(
            DB.XYZ(base_point.X + SQUARE_EDGE_LENGTH, base_point.Y, base_point.Z),
            DB.XYZ(base_point.X + SQUARE_EDGE_LENGTH, base_point.Y + DIRECTION, base_point.Z)
            )
    )
    cloop.Append(
        DB.Line.CreateBound(
            DB.XYZ(base_point.X + SQUARE_EDGE_LENGTH, base_point.Y + DIRECTION, base_point.Z),
            DB.XYZ(base_point.X, base_point.Y + DIRECTION, base_point.Z)
            )
    )
    cloop.Append(
        DB.Line.CreateBound(
            DB.XYZ(base_point.X, base_point.Y + DIRECTION, base_point.Z),
            DB.XYZ(base_point.X, base_point.Y, base_point.Z)
            )
    )

    DB.FilledRegion.Create(doc,
                           fr_type.Id,
                           doc.ActiveView.Id,
                           EA_UTILITY.list_to_system_list([cloop], type = "CurveLoop"))


def make_swatch(index, fr_type):
    row = 0 + (index / MAX_WIDTH)
    col = index - (MAX_WIDTH * row)
    base_point = DB.XYZ(col * SQUARE_EDGE_LENGTH, row * (GAP + DIRECTION), 0)
    make_title(base_point, fr_type)
    make_filledregion_element(base_point, fr_type)

"""    sample use





filledregion_types = revit.query.get_types_by_class(DB.FilledRegionType)
with revit.Transaction('Generate FilledRegion Swatched'):
    for idx, filledregion_type in enumerate(
            sorted(filledregion_types,
                   key=lambda x: revit.query.get_name(x))):
        make_swatch(idx, filledregion_type)
"""

def get_keynote_by_description(description):
    for item in ref_module.desired_filters:
        if description == ref_module.get_description(item):
            return ref_module.get_keynote(item)

################## main code below #####################
output = script.get_output()
output.close_others()


import imp
ref_module = imp.load_source("make walltype filter_script", r'{}\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135 Part2.pulldown\52_make walltype_filter and assign.pushbutton\make walltype filter_script.py'.format(EnneadTab.ENVIRONMENT.PUBLISH_FOLDER_FOR_REVIT))

GAP = EA_UTILITY.mm_to_internal(500)
SQUARE_EDGE_LENGTH = EA_UTILITY.mm_to_internal(3000)
MAX_WIDTH = 1  # number count per row
DIRECTION = 1 * SQUARE_EDGE_LENGTH       # OR -1


if "Legend" not in str(doc.ActiveView.ViewType):
    EA_UTILITY.dialogue(main_text = "Use it in a empty legend view only")
    script.exit()

if __name__ == "__main__":
    desired_filters = ref_module.desired_filters


    selected_filters = forms.SelectFromList.show(desired_filters,
                                                multiselect = True)

    if selected_filters is None:
        script.exit()

    t = DB.Transaction(doc, "make walltype legend")
    t.Start()
    fill_region_types = []
    for filter in selected_filters:
        fill_region_type_name = ref_module.get_description(filter)
        fill_region_color = ref_module.get_color(filter)
        region_type = get_region_type_by_name(fill_region_type_name)
        if region_type is None:
            region_type = create_region_type(fill_region_type_name, fill_region_color)
        else:
            update_fill_region_type_color(fill_region_type_name, fill_region_color)
        fill_region_types.append(region_type)


    for idx, filledregion_type in enumerate(sorted(fill_region_types, key = lambda x: get_keynote_by_description(x.LookupParameter("Type Name").AsString()).split(" ")[1], reverse = True)):
        make_swatch(idx, filledregion_type)

    t.Commit()
