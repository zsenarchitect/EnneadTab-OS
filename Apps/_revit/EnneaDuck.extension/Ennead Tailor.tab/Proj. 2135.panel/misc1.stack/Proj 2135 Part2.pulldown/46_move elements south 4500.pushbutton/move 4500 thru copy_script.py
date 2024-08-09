#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "NOT IN USE"
__title__ = "46A_move elements\nsouth 4500 thru copy/delete(NOT IN USE)"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:
uidoc = __revit__.ActiveUIDocument
selection_ids = uidoc.Selection.GetElementIds ()
#print selection_ids
t = DB.Transaction(doc, "move south 4500")
t.Start()
DB.ElementTransformUtils.CopyElements(doc, selection_ids, DB.XYZ(0,-EA_UTILITY.mm_to_internal(4500),0))
doc.Delete(selection_ids) #EA_UTILITY.list_to_system_list(selection_ids)
t.Commit()
