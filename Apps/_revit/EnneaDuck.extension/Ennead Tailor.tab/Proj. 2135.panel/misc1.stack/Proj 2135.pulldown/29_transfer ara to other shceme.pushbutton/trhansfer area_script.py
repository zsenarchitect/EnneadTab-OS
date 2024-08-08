__doc__ = "Get the area boundary lines and areas from one area scheme to another."
__title__ = "29_transfer area to other scheme"

from pyrevit import forms, revit, script #
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import Creation
import EA_UTILITY
import EnneadTab

doc = __revit__.ActiveUIDocument.Document # pyright: ignore



def get_matching_scheme_area_plan(view):
    def test_view(x):
        try:
            # print x.GenLevel.Name
            # print x.AreaScheme.Name
            if x.GenLevel.Name == view.GenLevel.Name and x.AreaScheme.Name == "GFA TEST Paula":
                # print "find"*20
                return True
            return False
        except:
            return False

    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    return filter(test_view, all_views)[0]



def process_view(view):

    def match_property(para_name, source, target):
        try:
            target.LookupParameter(para_name).Set(source.LookupParameter(para_name).AsString())
        except:
            target.LookupParameter(para_name).Set(source.LookupParameter(para_name).AsDouble())
        pass

    def transfer_area(area):
        area_location = area.Location.Point
        insert_location = DB.UV(area_location.X, area_location.Y)
        new_area = doc.Create.NewArea(target_view, insert_location)
        # print "new area created"

        para_names = ["MC_$Discount Ratio","Area Department", "Area Layout Function", "MC_$BuildingID"]
        for para_name in para_names:
            match_property(para_name, area, new_area)


    def transfer_boundary(boundary_line):
        ref_crv= boundary_line.Location.Curve
        new_area_boundary = doc.Create.NewAreaBoundaryLine(target_view.SketchPlane, ref_crv, target_view)



    target_view = get_matching_scheme_area_plan(view)


    boundary_lines = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_AreaSchemeLines).ToElements()
    map(transfer_boundary, boundary_lines)


    areas = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()
    # print len(areas)
    map(transfer_area, areas)


    pass
################## main code below #####################
output = script.get_output()
output.close_others()

selection = revit.get_selection()
#GET SELECTED VIEWS
views = selection



#PROCESS EACH VIEW
t = DB.Transaction(doc, "transfer area")
t.Start()
map(process_view, views)
t.Commit()
