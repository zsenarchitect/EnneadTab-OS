#!/usr/bin/python
# -*- coding: utf-8 -*-


__doc__ = "Basic area summery checker that update the data in special calculator. \n\nThis is also hooked to the sync event for this project."
__title__ = "All In One Checker"

# from pyrevit import forms #
from pyrevit import script
# from pyrevit import revit #
# import EA_UTILITY
import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore  
# from Autodesk.Revit import UI # pyright: ignore
try:
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
except:
    pass

CALCULATOR_FAMILY_NAME = "USF Calculator"
AREA_SCHEME_NAME = "Usable Area"
PARA_TRACKER_NAMES = ["(NON) USABLE",
                      "(NON) COMMON",
                      "(NON) COMMON-MECH",
                      "USABLE",
                      "USABLE MECH"]# maybe make it a ordered-dict to store the color setting.
LEVEL_NAMES = [] # in the setting file to set which level to run calc
CALCULATOR_VIEW_NAME = "EnneadTab Area Calculator Collection"

"""


for future abstract version, can process such that calculator family 
is opened by familymamager and validate to have such para meters. 

if famioly not found, will copy to dump folder and open.

If missing, will add missing parameter as area type
Load back to project

if symbol not activated. duplicate type until the all name of type match the names of level to check, place at EA_SPECIAL VIEW. Delete types who name is not in LevelNames list

create a schedule with defined rules(get viewschedule.definition, then add field, and set order)



some of the step need to be shared by seting maker.
The setting of the profile is saved in a L drive dict by project name
"""


class InternalCheck:
    """the main class for hosting method about area summery
    """

    def __init__(self, doc, show_log):
        self.doc = doc
        self.show_log = show_log

        # dict key = level name, this refer to the areadata obj, not calculaotr familyinstance
        self.area_data_collector = dict()
        # potentioally can use the AreaData class dict for future version


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def run_check(self):

        # get all the areas
        all_areas = DB.FilteredElementCollector(self.doc).OfCategory(
            DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
        all_areas = filter(lambda x: x.AreaScheme.Name ==
                           AREA_SCHEME_NAME, all_areas)

        # add info to dataItem
        for area in all_areas:
            level = area.Level
            if level:
                level_name = level.Name
                if level_name not in self.area_data_collector:
                    self.area_data_collector[level_name] = AreaData(level_name)

                # self.area_data_collector[level_name].source_areas.append(area)
                area_name = area.LookupParameter("Name").AsString()
                temp_data = self.area_data_collector[level_name]
                if area_name == "(NON) USABLE":
                    temp_data.area_non_usable += area.Area
                elif area_name == "(NON) COMMON":
                    temp_data.area_non_common += area.Area
                elif area_name == "(NON) COMMON-MECH":
                    temp_data.area_non_common_mech += area.Area
                elif area_name == "USABLE":
                    temp_data.area_usable += area.Area
                elif area_name == "USABLE MECH":
                    temp_data.area_usable_mech += area.Area
                else:

                    if self.show_log:
                        print("This area is unclear about usability.--->{}".format(
                            output.linkify(area.Id, title=area.LookupParameter("Name").AsString)))
                    else:
                        print(
                            "You have area unclear about usability.---> Run in tailor mode to find out which.")

        # for each data item, get the calcator family and update content
        t = DB.Transaction(self.doc, __title__)
        t.Start()
        for level_name in self.area_data_collector:
            if self.show_log:
                print(level_name)
            temp_data = self.area_data_collector[level_name]

            # get actual calculator familyinstances
            calculators = get_calculators_by_level_name(self.doc, level_name)

            if calculators:
                calculators = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(
                    calculators)
                for calculator in calculators:
                    # get the content
                    calculator.LookupParameter("Level_Name").Set(level_name)
                    calculator.LookupParameter(
                        "Usable").Set(temp_data.area_usable)
                    calculator.LookupParameter("Usable Mech").Set(
                        temp_data.area_usable_mech)
                    calculator.LookupParameter("Non Usable").Set(
                        temp_data.area_non_usable)
                    calculator.LookupParameter("Non Common").Set(
                        temp_data.area_non_common)
                    calculator.LookupParameter("Non Common Mech").Set(
                        temp_data.area_non_common_mech)

            else:
                if self.show_log:
                    print("No calculator found for level: {}".format(level_name))
                else:
                    print(
                        "No calculator found for level. Run in tailor mode to find out which.")
        t.Commit()


def get_all_calcuator_types(doc):
    all_symbol_types = DB.FilteredElementCollector(doc).OfCategory(
        DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
    return filter(lambda x: x.FamilyName == CALCULATOR_FAMILY_NAME, all_symbol_types)


def get_calculators_by_level_name(doc, level_name):

    return filter(lambda x: x.LookupParameter("Type Name").AsString() == level_name, get_all_calcuator_types(doc))


class AreaData:
    """the main class for holding area data on each level."""
    data_collection = dict()

    def __init__(self, level_name):
        self.level = level_name
        # self.source_areas = []
        self.area_usable = 0
        self.area_usable_mech = 0
        self.area_non_usable = 0
        self.area_non_common = 0
        self.area_non_common_mech = 0

    @classmethod
    def get_data(cls, level_name):
        key = level_name
        if key in cls.data_collection:
            return cls.data_collection[key]
        instance = AreaData(level_name)

        cls.data_collection[key] = instance
        return instance

    def update(self, area_name, area):
        if not hasattr(self, area_name):
            setattr(self, area_name, area)
            return
        
        current_area = getattr(self, area_name)
        setattr(self, area_name, current_area + area)

@EnneadTab.ERROR_HANDLE.try_catch_error
def all_in_one_checker(doc, show_log):
    """this is the main doc
    passing doc and show_log para to make sure using this as button VS using it
    during sync event hook can both work"""

    InternalCheck(doc, show_log).run_check()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    all_in_one_checker(doc, show_log=True)

    # record usage data to minbank
    ENNEAD_LOG.use_enneadtab(
        coin_change=20, tool_used=__title__.replace("\n", " "), show_toast=True)
