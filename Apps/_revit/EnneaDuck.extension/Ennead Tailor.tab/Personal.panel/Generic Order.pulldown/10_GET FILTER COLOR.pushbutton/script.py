__doc__ = "Print out the filter override surface foreground pattern color for the current view."


from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:

print(revit.active_view)
view = revit.active_view
filters = list(view.GetFilters())
filters.sort(key = lambda f: revit.doc.GetElement(f).Name)
for f in filters:
    filter_obj = view.GetFilterOverrides(f)
    print("********")
    print(revit.doc.GetElement(f).Name)
    try:
        color = filter_obj.SurfaceForegroundPatternColor
        print(color.Red, color.Green, color.Blue)
    except:
        continue
