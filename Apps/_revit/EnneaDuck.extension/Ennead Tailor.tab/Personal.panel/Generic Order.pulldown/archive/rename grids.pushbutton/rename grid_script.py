__doc__ = "Replace _ with - in grid names"
__title__ = "rename Grids"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()

grids = DB.FilteredElementCollector(revit.doc).OfClass(DB.Grid).WhereElementIsNotElementType().ToElements()


with revit.Transaction("rename grid"):
    for grid in grids:

        grid.Name = grid.Name.replace("_", "-")
