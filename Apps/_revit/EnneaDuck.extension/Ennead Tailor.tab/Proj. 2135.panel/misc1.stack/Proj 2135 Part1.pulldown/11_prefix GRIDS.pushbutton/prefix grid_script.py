__doc__ = "Prefix grid name with 'temp'"
__title__ = "11_prefix grids"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()


grids = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()


prefix = "temp"
with revit.Transaction("prefix views"):

    for grid in grids:

        if "N4" in grid.Name:
            grid.Name = "{}_{}".format(prefix , grid.Name)
        #view.Name = view.Name.split("check")[1]
