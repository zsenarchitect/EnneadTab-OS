#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Find the nearest level by boundingbox lowest Z, then apply vent level as Comments"
__title__ = "89_identify_level_for_cw_panel"

# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def get_level_by_z(z):
        #  get all levels
    levels = list(DB.FilteredElementCollector(doc).OfClass(DB.Level).WhereElementIsNotElementType().ToElements())
    levels = filter(lambda x: x.Name not in ["N3 - T.O.SCREEN WALL", "N3 - PODIUM PARAPET"], levels)
    levels.sort(key = lambda x: abs(z - x.Elevation) )
    return levels[0]

def identify_level_for_cw_panel():
    pass

    # get all curtain panel of type that have bowtie
    all_panels = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()

    def is_check_panel(x):
        if not hasattr(x, "Symbol"):
            return False
        if x.Symbol.Family.Name != "Bili_Flat_Main":
            return False

        if x.LookupParameter("#is_triface pier casing").AsInteger() == 0:
            return False
        return True

    all_panels = filter(is_check_panel, all_panels)
    all_panels.sort(key = lambda x: x.get_BoundingBox(doc.ActiveView) .Min.Z, reverse = True)



    t = DB.Transaction(doc, __title__)
    t.Start()
    for panel in all_panels:


        # get boundingbox z height
        panel_z = panel.get_BoundingBox(doc.ActiveView) .Min.Z

        # find nearest levels
        near_level = get_level_by_z(panel_z)


        if panel.LookupParameter("#is_arch B").AsInteger():
            print("\n####################")
            print("{}".format(output.linkify(panel.Id)))
            print(near_level.Name)

            moudle_note = "_{} module".format(panel.LookupParameter("Width").AsValueString ())

            if panel.LookupParameter("#is_flip casing").AsInteger():
                # dealing with arch in self scope
                pass # unchanged
            else:
                # dealling with bowtie on next panel


                if panel.LookupParameter("is_terminal panel_start").AsInteger():
                    moudle_note = "_1600 module"
                if panel.LookupParameter("is_terminal panel_end").AsInteger():
                    moudle_note = "_1300 module"
            panel.LookupParameter("Comments").Set("Vent Level_" + near_level.Name + moudle_note)
        else:
            panel.LookupParameter("Comments").Set("")


    t.Commit()

    print("################################################ Finished")

    # apply name to comments

    """

    $$$$$$$$$$$$$$$$$$$

    """
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
"""
    phase_provider = DB.ParameterValueProvider( DB.ElementId(DB.BuiltInParameter.ROOM_PHASE))
    phase_rule = DB.FilterElementIdRule(phase_provider, DB.FilterNumericEquals(), phase.Id)
    phase_filter = DB.ElementParameterFilter(phase_rule)
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WherePasses(phase_filter).WhereElementIsNotElementType().ToElements()
    return all_rooms
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    identify_level_for_cw_panel()
    




