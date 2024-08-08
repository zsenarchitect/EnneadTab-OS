__doc__ = "Filter selection for panels with 'is_double pane spandrel' and 'is_louver lower' checked."
__title__ = "Find Louvers"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()


selection = revit.get_selection()
panels = []
for item in selection:
    if item.LookupParameter("is_double pane spandrel").AsInteger() == 1 and  item.LookupParameter("is_louver lower").AsInteger() == 1:
        panels.append(item)

revit.get_selection().set_to(panels)
