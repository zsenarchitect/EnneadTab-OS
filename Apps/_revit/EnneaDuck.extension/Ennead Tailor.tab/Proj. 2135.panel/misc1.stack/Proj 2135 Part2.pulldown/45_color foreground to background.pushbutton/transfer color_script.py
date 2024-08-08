#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Make material foreground graphic to background graphic"
__title__ = "45_transfer material color background"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def get_solid_fill_pattern_id():
    fill_patterns = DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement).WhereElementIsNotElementType().ToElements()
    for fill_pattern in fill_patterns:
        if fill_pattern.GetFillPattern().IsSolidFill:
            return fill_pattern.Id
    return None



def modify_material_surface(material):
    print("---surface background fix, working on: {}".format(material.Name))
    try:
        material.SurfaceBackgroundPatternColor  = material.SurfaceForegroundPatternColor
        material.SurfaceBackgroundPatternId = material.SurfaceForegroundPatternId
        material.SurfaceForegroundPatternId = DB.ElementId(-1)
        #material.SurfaceForegroundPatternId = get_solid_fill_pattern_id()
    except Exception as e:
        print("fail, error = {}".format(e))
    pass

def modify_material_cut(material):
    print("---cut background fix, working on: {}".format(material.Name))
    try:
        material.CutBackgroundPatternColor  = material.CutForegroundPatternColor
        material.CutBackgroundPatternId = material.CutForegroundPatternId
        material.CutForegroundPatternId = DB.ElementId(-1)
        #material.SurfaceForegroundPatternId = get_solid_fill_pattern_id()
    except Exception as e:
        print("fail, error = {}".format(e))
    pass

def get_bad_material():
    temp_surface_problem = []
    temp_cut_problem = []
    my_materials = list(DB.FilteredElementCollector(doc).OfClass(DB.Material).WhereElementIsNotElementType().ToElements())
    my_materials.sort(key = lambda x: x.Name)
    print("those materials has background pattern setting as None")
    for material in my_materials:
        #print "{}:{}".format(material.Name, material.SurfaceBackgroundPatternId)

        if material.SurfaceBackgroundPatternId.IntegerValue == -1:
            print(material.Name)
            temp_surface_problem.append(material)

        if material.CutBackgroundPatternId.IntegerValue == -1:
            print(material.Name)
            temp_cut_problem.append(material)
    return temp_surface_problem, temp_cut_problem

################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:


#print_bad_material()

"""
my_materials = list(DB.FilteredElementCollector(doc).OfClass(DB.Material).WhereElementIsNotElementType().ToElements())
my_materials.sort(key = lambda x: x.Name)
"""

my_materials_surface_problem, my_materials_cut_problem = get_bad_material()
selected_materials_surface = forms.SelectFromList.show(my_materials_surface_problem,
                                            name_attr = "Name",
                                            multiselect = True,
                                            title = "pick materials",
                                            button_name='transfer surface background color to foreground')

selected_materials_cut = forms.SelectFromList.show(my_materials_cut_problem,
                                            name_attr = "Name",
                                            multiselect = True,
                                            title = "pick materials",
                                            button_name='transfer cut background color to foreground')

if selected_materials_surface is None and selected_materials_cut is None:
    script.exit()
res = EA_UTILITY.dialogue(options = ["Yes", "No"], main_text = "close and sync after done?")
doc.Save()
# modify each template
t = DB.Transaction(doc, "trnsfer materials")
t.Start()
map(modify_material_surface, selected_materials_surface)
map(modify_material_cut, selected_materials_cut)
t.Commit()

if res == "Yes":
    EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close()
