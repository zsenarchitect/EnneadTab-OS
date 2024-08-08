from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms


__doc__ = "xxx"

sel_sheets = forms.select_sheets(title='Select Sheets That You Want To Find User Keynotes.')

output = script.get_output()

def get_special_keynotes_in_sheets(sheets):
    user_keynotes_tags = []
    for sheet in sheets:
        viewports = sheet.GetAllViewports()
        for viewport in viewports:
            view_id = revit.doc.GetElement(viewport).ViewId
            keynotes_tags = DB.FilteredElementCollector(revit.doc,view_id)\
              .OfCategory(DB.BuiltInCategory.OST_KeynoteTags)\
              .WhereElementIsNotElementType()\
              .ToElements()
            for tag in keynotes_tags:

                if tag.Parameter[DB.BuiltInParameter.KEY_VALUE].AsString() == "CW-7A":
                    user_keynotes_tags.append(tag)
    return user_keynotes_tags


seperation = "---------------"

if sel_sheets:
    if len(sel_sheets) > 0:
        user_keynotes_tags = get_special_keynotes_in_sheets(sel_sheets)
    else:
        forms.alert("No Sheet Selected. \nCancelled.")
        script.exit()
else:
    forms.alert("Cancelled")
    script.exit()


if len(user_keynotes_tags)>0:
    for idx, tag in enumerate(user_keynotes_tags):
        id = tag.Id
        key_value = "Key Value = " + tag.Parameter[DB.BuiltInParameter.KEY_VALUE].AsString()
        key_text = "Keynote Text = " + tag.Parameter[DB.BuiltInParameter.KEYNOTE_TEXT].AsString()
        parent_view = tag.OwnerViewId
        print ("{}: tag Id = {}-->{}".format(idx+1,tag.Id,output.linkify(tag.Id, title = "Go To Tag")))
        print(key_value)
        print(key_text)
        print("Found in this view: {} :-->{}".format(revit.doc.GetElement(parent_view).Name,output.linkify(parent_view, title = "Go To View")))
        print(seperation)


print('{0} KEYNOTE(S) FOUND IN SELECTED SHEETS.'.format(len(user_keynotes_tags)))
