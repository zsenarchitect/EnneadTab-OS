#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Give elements in selected design options a color in selected views, so you can visualize what is inside each option."
__title__ = "Color-Code\nDesign Option"
__tip__ = True
import random
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #

import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

class Solution:
    
    @ERROR_HANDLE.try_catch_error()
    def color_design_option(self):

        self.views = forms.select_views(multiple = True, button_name = 'Select View. When nothing is selected, it will work on active view')
        if not self.views:
            self.views = [doc.ActiveView]




        design_options = DB.FilteredElementCollector(doc).OfClass(DB.DesignOption).ToElements()


        class MyOption(forms.TemplateListItem):
            def get_option_set_name(self):
                return doc.GetElement(self.Parameter[DB.BuiltInParameter.OPTION_SET_ID].AsElementId()).Name

            @property
            def name(self):
                set_name = self.get_option_set_name()
                return "[{}]  {}".format(set_name, self.Name)

        ops = [MyOption(x) for x in design_options]
        ops.sort(key = lambda x: x.get_option_set_name())
        self.design_options = forms.SelectFromList.show(ops,
                                                    multiselect = True,
                                                    button_name = 'Select option. When nothing is selected, all elements restore default',
                                                    title = "I will give random color per desing option. ")
        if not self.design_options:

            self.reset_graphic()
            return


        self.solid_id = REVIT_SELECTION.get_solid_fill_pattern_id(doc)
        self.color_map = dict()
        for design_option in design_options:
            self.color_map[design_option.Id] = DB.Color(int(100*random.random()) + 100,
                                                        int(100*random.random()) + 100,
                                                        int(100*random.random()) + 100)

        t = DB.Transaction(doc, __title__)
        t.Start()
        map(lambda x: self.process_design_option(x), self.design_options)
        t.Commit()

    def reset_graphic(self):

        t = DB.Transaction(doc, __title__)
        t.Start()
        elements = list(DB.FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements())
        setting = DB.OverrideGraphicSettings ()
        for view in self.views:
            print ("- Resetting View = {}".format(view.Name))
            try:
                map(lambda x: view.SetElementOverrides (x.Id, setting), elements)
            except Exception as e:
                print (e)
        t.Commit()



    def process_design_option(self, design_option):


        elements = list(DB.FilteredElementCollector(doc).ContainedInDesignOption(design_option.Id).WhereElementIsNotElementType().ToElements())

        def is_good_element(x):
            for check in ["Panel", "Sketch", "CurtainGridLine", "Dimension", "ElementType","StairsLanding","StairsRun", "FamilySymbol"]:
                #print str(x.GetType())
                if check in str(x.GetType()):
                    # elements.remove(x)
                    #print "-"*200
                    return False
            return True


        elements = filter(lambda x: is_good_element(x), elements)


        R = self.color_map[design_option.Id].Red
        G = self.color_map[design_option.Id].Green
        B = self.color_map[design_option.Id].Blue

        color = DB.Color(R, G, B)
        color_line = DB.Color(R - 50, G - 50, B - 50)

        setting = DB.OverrideGraphicSettings ()

        setting.SetCutForegroundPatternColor  (color)
        setting.SetCutForegroundPatternId (self.solid_id)
        setting.SetCutLineColor (color_line)
        setting.SetSurfaceForegroundPatternId (self.solid_id)
        setting.SetSurfaceForegroundPatternColor (color)
        setting.SetProjectionLineColor (color_line)

        set_name = doc.GetElement(design_option.Parameter[DB.BuiltInParameter.OPTION_SET_ID].AsElementId()).Name
        print ("\n\nChecking design option: [{}]-->{}: {} Elements".format(set_name, design_option.Name, len(elements)))
        output.freeze()
        for i, element in enumerate(elements):
            if element.Category is None:
                print ("{} - {}".format(i + 1, output.linkify(element.Id)))
            else:
                print ("{} - {}".format(i + 1, output.linkify(element.Id, title = element.Category.Name)))
        output.unfreeze()
        print ("\nRGB = {},{},{}\n".format(R,G,B))

        for view in self.views:
            print ("- View = {}".format(output.linkify(view.Id, title = view.Name)))
            try:
                map(lambda x: view.SetElementOverrides (x.Id, setting), elements)
            except Exception as e:
                print ("\t\t{}\n".format(e))






################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    Solution().color_design_option()
    
