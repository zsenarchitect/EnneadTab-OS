__doc__ ="""
This function renames views in Revit based on their associated level and name. It first selects the views to be renamed. \
It then loops through each view in the selection and extracts the associated level and key from the view name. The key \
is used to identify the type of view, and is used in the new view name. The associated level and key are combined to form \
a new detail number for the view, which is set as the view's "Detail Number" parameter. If the associated level cannot be \
extra"""
__title__ = "51_rename detail num"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()

views = forms.select_views(use_selection = True)


with revit.Transaction("RENAME views"):

    for view in views:
        level = view.LookupParameter("Associated Level").AsString()
        #print view.LookupParameter("Detail Number").AsString()
        key = ""
        if "GFA" in view.Name:
            key = "GFA"
        if "Office Layout" in view.Name:
            key = "Office Layout"
        if "Discount Ratio" in view.Name:
            key = "Discount Ratio"



        try:
            detail_num = level.split(" - ")[0] + " " + level.split(" - ")[1] + "_" + key
        except:
            detail_num = view.LookupParameter("Detail Number").AsString() + "_temp"
        view.LookupParameter("Detail Number").Set(detail_num)
        #view.Name = prefix + "_" + view.Name
        #view.Name = view.Name.split("check")[1]
