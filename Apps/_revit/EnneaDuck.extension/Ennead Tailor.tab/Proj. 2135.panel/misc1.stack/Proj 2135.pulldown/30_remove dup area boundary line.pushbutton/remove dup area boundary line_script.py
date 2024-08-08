__doc__ = "Remove duplicated the area boundary line for each view."
__title__ = "30_remove dup area boundary line"

from pyrevit import forms, revit, script #
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import Creation
import EA_UTILITY
import EnneadTab

doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def current_warning_count():
    return len(doc.GetWarnings())

def process_view(view):

    def get_all_boundary():
        return DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_AreaSchemeLines).ToElements()

    def fix_boundary(boundary_line):
        try:
            crv = boundary_line.Location.Curve
        except:
            return
        for other_line in get_all_boundary():
            if other_line.Id == boundary_line.Id:
                continue
            other_crv = other_line.Location.Curve
            result = crv.Intersect(other_crv)
            if str(result) != "Equal":
                continue
            if crv.ApproximateLength < other_crv.ApproximateLength:
                continue
            try:
                doc.Delete(other_line.Id)
                print("overlaping line deleted, now total warning count = {}".format(current_warning_count()))
                # EA_UTILITY.show_toast(title = "deleting")
            except:
                pass
            finally:
                # print result
                pass



    boundary_lines = get_all_boundary()
    print("---------Working on view: {}".format(view.Name))
    EA_UTILITY.show_toast(title = "Working on view: {}".format(view.Name))
    map(fix_boundary, boundary_lines)



################## main code below #####################
output = script.get_output()
output.close_others()

selection = revit.get_selection()
#GET SELECTED VIEWS
if len(selection) == 0:
    forms.alert("select at least one view from project browser")
    script.exit()

views = selection


warning_num = current_warning_count()
#PROCESS EACH VIEW
t = DB.Transaction(doc, "remove dup area line")
t.Start()
map(process_view, views)
t.Commit()
EA_UTILITY.show_toast(title = "Tool finished!!!", message = "{} warnings reduced".format(warning_num - current_warning_count() ))
print("Tool finished")
print("{} warnings reduced".format(warning_num - current_warning_count() ))

# EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close()
