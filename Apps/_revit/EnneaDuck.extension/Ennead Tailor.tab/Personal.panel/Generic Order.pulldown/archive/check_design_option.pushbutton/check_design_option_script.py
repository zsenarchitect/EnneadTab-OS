#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "See what is inside your design option by colorize them."
__title__ = "Check Design Option(Depreciated)"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #

import ENNEAD_LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
import random
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

class Solution:
    def __init__(self):
        pass


    def process_view(self, view, option):
        print("\n####### View = {}".format(view.Name))
        set_name = doc.GetElement(option.Parameter[DB.BuiltInParameter.OPTION_SET_ID].AsElementId()).Name
        print("Checking design option: [{}]-->{}".format(set_name, option.Name))
        R = self.color_map[option.Id].Red
        G = self.color_map[option.Id].Green
        B = self.color_map[option.Id].Blue
        print("RGB = {},{},{}".format(R,G,B))

        def enhance_color(x):
            return min(256, int(float(x * 1.1)))
        line_color = DB.Color(enhance_color(R),
                            enhance_color(G),
                            enhance_color(B))


        elements = DB.FilteredElementCollector(doc, view.Id).WhereElementIsNotElementType().ToElements()
        elements = filter(lambda x: x.DesignOption is not None , elements)
        elements = filter(lambda x: x.DesignOption.Id == option.Id, elements)
        #print elements
        color = self.color_map[option.Id]
        setting = DB.OverrideGraphicSettings ()
        setting.SetSurfaceForegroundPatternColor (color)
        setting.SetSurfaceForegroundPatternId  (self.solid_id)
        setting.SetSurfaceBackgroundPatternColor (color)
        setting.SetSurfaceBackgroundPatternId  (self.solid_id)

        setting.SetCutForegroundPatternColor (color)
        setting.SetCutForegroundPatternId  (self.solid_id)
        setting.SetCutBackgroundPatternColor (color)
        setting.SetCutBackgroundPatternId  (self.solid_id)

        setting.SetProjectionLineColor (line_color)
        setting.SetCutLineColor (line_color)
        for element in elements:
            view.SetElementOverrides (element.Id, setting)



    def check_design_option(self):
        design_options = DB.FilteredElementCollector(doc).OfClass(DB.DesignOption).ToElements()


        class MyOption(forms.TemplateListItem):
            def get_option_set_name(self):
                return doc.GetElement(self.Parameter[DB.BuiltInParameter.OPTION_SET_ID].AsElementId()).Name

            @property
            def name(self):
                set_name = self.get_option_set_name()
                return "[{}]-->{}".format(set_name, self.Name)

        ops = [MyOption(x) for x in design_options]
        ops.sort(key = lambda x: x.get_option_set_name())
        design_options = forms.SelectFromList.show(ops,
                                        multiselect = True,
                                        button_name = 'Select option to check',
                                        title = "What sets to visulize?")

        if not design_options:
            return

        #print design_options
        self.solid_id = EnneadTab.REVIT.REVIT_SELECTION.get_solid_fill_pattern_id(doc)
        self.color_map = dict()
        for design_option in design_options:
            self.color_map[design_option.Id] = DB.Color(random.randrange(180, 256),
                                                        random.randrange(180, 256),
                                                        random.randrange(180, 256))


        view = doc.ActiveView
        views = forms.select_views(title = "Which views to visualize design option?",
                                    multiple = True)
        if not views:
            return

        t = DB.Transaction(doc, "highlight design option")
        t.Start()
        for view in views:
            map(lambda x: self.process_view(view, x), design_options)
        t.Commit()

"""
def try_catch_error(func):
    def wrapper(*args, **kwargs):
        print("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            return func(*args, **kwargs)
        except Exception as e:
            print(str(e))
            return "Wrapper func for EA Log -- Error: " + str(e)
    return wrapper
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    my_solution = Solution()
    my_solution.check_design_option()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__, show_toast = True)
