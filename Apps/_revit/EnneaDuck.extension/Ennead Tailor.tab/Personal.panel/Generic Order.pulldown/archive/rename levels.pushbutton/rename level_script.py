__doc__ = "Remove '_' in level names, and replace 'C' to 'E'"
__title__ = "Rename Level"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()

levels = DB.FilteredElementCollector(revit.doc).OfClass(DB.Level).WhereElementIsNotElementType().ToElements()


with revit.Transaction("rename level"):
    for level in levels:
        #print level.Name
        #print level.Name.replace("_", "")
        #level.Name = level.Name.replace("_LEVEL", " - LEVEL")
        level.Name = level.Name.replace("_", "")
        level.Name = level.Name.replace("C", "E")
