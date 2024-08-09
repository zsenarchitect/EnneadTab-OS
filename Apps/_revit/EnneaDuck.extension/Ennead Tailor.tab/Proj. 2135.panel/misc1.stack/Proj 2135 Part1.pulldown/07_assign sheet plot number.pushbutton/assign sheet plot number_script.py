__doc__ = "Assign plot ID to all sheet, floor, level and grid elements in project. This is critical for having a accurate shcedule from linked file."
__title__ = "07_sheet, floor, level and grid plot number"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()

IDs = ["N3", "N4", "N5", "N6", "0_Site"]
target = forms.ask_for_one_item(IDs,  prompt="What plot Id to use?", title=None)
#sheets = forms.select_sheets()
sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
grids = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
levels = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
floors = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()

with revit.Transaction("update plot ID for sheets and grids"):
    map(lambda x: x.LookupParameter("MC_$PlotID").Set(target), sheets)
    map(lambda x: x.LookupParameter("MC_$PlotID").Set(target), grids)
    map(lambda x: x.LookupParameter("MC_$PlotID").Set(target), levels)
    #map(lambda x: x.LookupParameter("MC_$PlotID").Set(target), floors)
    """
    for sheet in sheets:
        sheet.LookupParameter("MC_$PlotID").Set(target)
    """
