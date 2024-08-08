__doc__ = "Shift Detail NUmber on viewport of current sheet by adding 10"


from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:

print(revit.active_view)
with revit.Transaction("add 10"):
    for view_id in revit.active_view.GetAllViewports():
        view = revit.doc.GetElement(view_id)# this view is actually viewport class, not view class
        if revit.doc.GetElement(view.ViewId).ViewType.ToString() == "Legend":
            continue
        print(revit.doc.GetElement(view.ViewId).Name)
        refill_title = False
        detail_num_para_id = DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
        detail_num = 110 + int(view.Parameter[detail_num_para_id].AsString()) #get view detail num
        print(detail_num)

        view.Parameter[detail_num_para_id].Set(str(detail_num))

    for view_id in revit.active_view.GetAllViewports():
        view = revit.doc.GetElement(view_id)# this view is actually viewport class, not view class
        if revit.doc.GetElement(view.ViewId).ViewType.ToString() == "Legend":
            continue
        print(revit.doc.GetElement(view.ViewId).Name)
        refill_title = False
        detail_num_para_id = DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
        detail_num = -100 + int(view.Parameter[detail_num_para_id].AsString()) #get view detail num
        print(detail_num)

        view.Parameter[detail_num_para_id].Set(str(detail_num))
