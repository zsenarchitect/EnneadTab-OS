__doc__ = "Pre-ppend 'room working_' to view name"
__title__ = "Rename selected views as working view"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()

views = forms.select_views()

with revit.Transaction("rename view as working view"):
    for view in views:
        new_name = "room working_" + view.Name.split("(")[0]
        view.Name = new_name
