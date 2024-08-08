__doc__ = "Force to make all sheets check this 'Appears In Sheet List'. You are suggested to always use other method to filter sheets in schedule, becasue a QAQC sheet schedule should be able to see every sheet, including the onces not for documentation."
__title__ = "41_ check if sheet on schedule"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()


sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

sheets = sorted(sheets)
t = DB.Transaction(revit.doc, "Fix up appear in sheet schedule")
t.Start()
print("Sheets below native checkbox are not on.")
for sheet in sheets:
    if not sheet.LookupParameter("Appears In Sheet List").AsInteger():
        print("{} - {}".format(sheet.SheetNumber, sheet.Name))
        sheet.LookupParameter("Appears In Sheet List").Set(1)
        sheet.LookupParameter("Sheet Note").Set("NOT ISSUE for 05/27")


t.Commit()
