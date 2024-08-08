#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Make sure all egress stair has consistent width on run, and push that to calculator stair width"
__title__ = "(Depreciated)Format Egress Stairs"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
try:
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
except:
    pass


def get_all_calcuator_types(doc):
    all_symbol_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
    return filter(lambda x: x.FamilyName == "Stair Life Safety Calculator", all_symbol_types)


def get_calculator_type_by_stair_id(doc, stair_id):
    for type in get_all_calcuator_types(doc):
        type_name =  type.LookupParameter("Type Name").AsString()
        if type_name == stair_id:
            return type

def format_stairs(doc, show_log = True):
    t = DB.Transaction(doc, __title__)
    t.Start()

    all_stairs = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()
    all_stairs = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_stairs)
    
    bad_areas = set()
    for stair in all_stairs:
        stair_id = stair.LookupParameter("Egress_Id").AsString()
        if not stair_id:
            print ("\n!!!!!Checking no egress Id stair: {}. Talk to Sen Zhang for details for what it means.".format(output.linkify(stair.Id)))
        else:
            if show_log:
                
                print ("\nChecking stair: {}".format(stair_id))
        # fix area that does not have discount factor data
        runs = [doc.GetElement(x) for x in stair.GetStairsRuns()]
     
        max_width = runs[0].ActualRunWidth
        if show_log: 
            print (max_width)
        for run in runs:
            if not  run.ActualRunWidth == max_width:
                print( "--This stair has variring  run width--->{}. Talk to Sen Zhang to understand what it means.".format(output.linkify(run.Id)))
        
        
        
        
        calculator_type = get_calculator_type_by_stair_id(doc, stair_id)
        if not calculator_type:
            print ("Cannot find a calculator for : {}.  Talk to Sen Zhang to understand why.".format(stair_id))
            continue
        calculator_type.LookupParameter("Stair Width").Set(max_width)
    t.Commit()

  

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    format_stairs(doc)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)






