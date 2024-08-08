#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "For selected ADP componenets that have been placed. Run 'Repeat' Command for all of them. This saves you huge time on waiting for recalculating patterned placement."
__title__ = "36_repeat ADP"

# from pyrevit import forms #
from pyrevit import script, revit #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


################## main code below #####################
output = script.get_output()
output.close_others()

"""
adps = DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WhereElementIsNotElementType().ToElements()
for x in adps:
    print(x)
print(len(adps))
script.exit()
"""
selection = revit.get_selection()
t = DB.Transaction(doc, "repeat ADP")
t.Start()
for el in selection:
    # print el.Name
    DB.ComponentRepeater.RepeatElements(doc, EA_UTILITY.list_to_system_list([el.Id]))
t.Commit()
