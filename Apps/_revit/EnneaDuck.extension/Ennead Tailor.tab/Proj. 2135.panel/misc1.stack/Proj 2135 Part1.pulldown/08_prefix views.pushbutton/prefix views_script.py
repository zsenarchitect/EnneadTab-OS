__doc__ = "Prefix user input text before view names. Good for organizing workings such as slab edge drawings and GFA drawings."
__title__ = "08_prefix views"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()

views = forms.select_views(use_selection = True)

prefix = forms.ask_for_string(promp = "prefix to add, auto add '_' after")
with revit.Transaction("prefix views"):

    for view in views:
        view.Name = prefix + "_" + view.Name
        #view.Name = view.Name.split("check")[1]
