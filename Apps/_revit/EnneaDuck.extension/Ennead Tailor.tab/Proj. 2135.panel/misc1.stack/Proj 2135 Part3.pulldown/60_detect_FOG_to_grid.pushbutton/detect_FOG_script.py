#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Detect the FOG of curtain to the nearest palleral grid line.\n\nThe \
result is ranked by how off the distance are to the nearest whole number.\n\n\
It also provide links to the problem curtain wall, and will attempt to create a \
working view to help you fix them."
__title__ = "60_detect_FOG"

from pyrevit import forms
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
import math
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def get_plan_view(name):
    views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    for view in views:
        if view.Name == name:
            return view

    levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).WhereElementIsNotElementType().ToElements()
    tallest_level = sorted(levels, key = lambda x: x.Elevation)[-1]
    #view = DB.ViewPlan.Create(doc, DB.ViewPlanType.FloorPlan.Id, tallest_level.Id)
    view_family_types = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
    for type in view_family_types:
        if type.FamilyName == "Floor Plan":
            break
    view = DB.ViewPlan.Create(doc, type.Id, tallest_level.Id)
    view.Name = name
    view.ViewTemplateId = DB.ElementId.InvalidElementId
    return view
    pass


def create_plan_view_from_walltype(walltype_name):
    view_name = "EnneadTab FOG Check_" + walltype_name
    view = get_plan_view(view_name)


    view_range = view.GetViewRange ()
    view_range.SetOffset(DB.PlanViewPlane.CutPlane, 0)
    #view_range.SetLevelId(DB.PlanViewPlane.ViewDepthPlane, DB.PlanViewRangeLevel.Unlimited)
    view_range.SetLevelId(DB.PlanViewPlane.ViewDepthPlane, view_range.Unlimited)
    view.SetViewRange (view_range)


    for cate in doc.Settings.Categories:
        if cate.Name in ["Walls", "Curtain Panels", "Grids", "Dimensions"]:

            view.SetCategoryHidden(cate.Id, False)
        else:
            if view.CanCategoryBeHidden(cate.Id):
                view.SetCategoryHidden(cate.Id, True)

    view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate)



    grids = list(DB.FilteredElementCollector(doc).OfClass(DB.Grid).WhereElementIsNotElementType().ToElements())
    walls = DB.FilteredElementCollector(doc).OfClass(DB.Wall).WhereElementIsNotElementType().ToElements()
    walls = filter(lambda x: x.WallType.LookupParameter("Type Name").AsString() == walltype_name, walls)

    el_ids = []
    el_ids.extend([x.Id for x in grids])
    el_ids.extend([x.Id for x in walls])
    for wall in walls:
        el_ids.extend(wall.CurtainGrid.GetPanelIds())

    view.IsolateElementsTemporary (EA_UTILITY.list_to_system_list(el_ids))



    try:
        view.LookupParameter("Views_$Group").Set("00_EA's_Little Helper")
        view.LookupParameter("Views_$Series").Set("FOG Check")
    except:
        pass




def is_parralel_to_wall(grid, wall):
    wall_crv = wall.Location.Curve
    if not hasattr(wall_crv, "Direction"):
        return False

    wall_dir = wall.Location.Curve.Direction
    grid_dir = grid.Curve.Direction
    angle = wall_dir.AngleTo(grid_dir)
    if math.sin(angle) > 0.001:
        return False
    projected_pt0_dist, projected_pt1_dist = get_end_pt_dist(grid, wall)
    if projected_pt0_dist - projected_pt1_dist < 0.0001:
        return True
    return False

def get_end_pt_dist(grid, wall):
    wall_crv = wall.Location.Curve
    #print wall_crv
    wall_pt0 = flaten_pt(wall_crv.GetEndPoint(0))
    wall_pt1 = flaten_pt(wall_crv.GetEndPoint(1))
    grid_crv = grid.Curve
    grid_crv.MakeUnbound()
    projected_pt0_dist = grid_crv.Project(wall_pt0).Distance
    projected_pt1_dist = grid_crv.Project(wall_pt1).Distance
    return projected_pt0_dist, projected_pt1_dist


def flaten_pt(pt):
    return DB.XYZ(pt.X, pt.Y, 0)

def get_min_dist_to_grid(wall, grids):
    dist_list = [get_end_pt_dist(x, wall)[0] for x in grids]
    dist_list.sort()
    if len(dist_list) > 0:
        return dist_list[0]
    return None


def process_wall(wall, tolerance):

    grids = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
    grids = filter(lambda x: is_parralel_to_wall(x, wall), grids)
    dist = get_min_dist_to_grid(wall, grids)
    if dist:
        #print "wall_type = {}---->{}".format(wall.WallType.LookupParameter("Type Name").AsString(),output.linkify(wall.Id))
        dist = EA_UTILITY.internal_to_mm(dist)
        #print "{}mm to near grid.".format(dist)


        #if 0.001 < dist % tolerance < (tolerance - 0.001):
        if 0.001 < get_mistake(dist, tolerance) < (tolerance - 0.001):

            #output.print_md("##{}mm off.".format(dist % tolerance))
            return (wall, dist)
        else:
            pass
            #print "{}mm off.".format(dist % 1)
    return None


def get_mistake(dist, tolerance):
    """
    int(dist /10) * 10 ----> this can round to nearesrt big int
    1502.56 ---> 1500
    1448.29 ---> 1500
    """
    """
    print(dist)
    print(dist / float(tolerance))
    print(int(dist / float(tolerance)))
    print(int(dist / float(tolerance)) * tolerance)
    """
    """
    print(dist)
    print(round(dist, -1))
    print(int(round(dist, -1)))
    """

    #intent = int(dist / float(tolerance)) * tolerance
    intent = int(round(dist, -1))
    diff = abs(intent - dist)
    return diff

def detect_FOG():
    wall_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
    wall_types = filter(lambda x: str(x.Kind) == "Curtain" , wall_types)
    class MyOption_simple(forms.TemplateListItem):
        @property
        def name(self):
            return "{}".format(self.item.LookupParameter("Type Name").AsString())

    selected_types = forms.SelectFromList.show([MyOption_simple(x) for x in wall_types],
                                                title = "Which wall types to inspect?",
                                                multiselect = True,
                                                button_name = 'Select Types to inspect')
    if selected_types is None:
        return

    tolerance = 10

    #output.show()
    print("detecting walls and grids...")
    # print get_mistake(1502.56, tolerance)
    # print get_mistake(1448.22, tolerance)
    #
    # return
    #output.freeze()

    selected_types = [x.LookupParameter("Type Name").AsString() for x in selected_types]
    walls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    #print walls[0].WallType.Kind
    walls = filter(lambda x: str(x.WallType.Kind) == "Curtain" and x.WallType.LookupParameter("Type Name").AsString() in selected_types, walls)
    important_walls = []
    for i, wall in enumerate(walls):
        output.update_progress(i, len(walls))
        if i % 20 == 0:
            #output.unfreeze()
            print("\n###{} of {}".format(i, len(walls)))
            #output.freeze()
        result = process_wall(wall, tolerance)
        if result:
            important_walls.append(result)




    #output.unfreeze()
    print("#"*20)

    # print important_walls[0]

    important_walls.sort(key = lambda x: get_mistake(x[1], tolerance))
    wall_type_dict = dict()
    for data in important_walls:
        wall_type = data[0].WallType.LookupParameter("Type Name").AsString()
        if wall_type in wall_type_dict.keys():
            wall_type_dict[wall_type] += 1
        else:
            wall_type_dict[wall_type] = 1


    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "[{}]:{}".format(self.item[1], self.item[0])

    #print important_walls
    #print wall_type_dict

    ops = [MyOption(x) for x in wall_type_dict.items()]


    selected_types = forms.SelectFromList.show(ops,
                                                multiselect = True,
                                                title = "Whose detail report to see and fix? Number means how many problem walls there are.",
                                                button_name = 'Select types to fix')
    if not selected_types:
        return
    #wall_types = list(set([x.WallType.LookupParameter("Type Name").AsString()] for x in important_walls))
    selected_types = [x[0] for x in selected_types]

    t = DB.Transaction(doc, "detect FOG")
    t.Start()
    map(create_plan_view_from_walltype, selected_types)
    t.Commit()


    important_walls = filter(lambda x: x[0].WallType.LookupParameter("Type Name").AsString() in selected_types, important_walls)
    for i, data in enumerate(important_walls):
        wall, dist = data
        print("\n###{} of {}".format(i, len(important_walls)))
        print("wall_type = {}---->{}".format(wall.WallType.LookupParameter("Type Name").AsString(),output.linkify(wall.Id)))
        print("{}mm to near grid.".format(dist))
        #output.print_md("##{}mm off.".format(dist % tolerance))
        output.print_md("##{}mm off.".format(get_mistake(dist, tolerance)))


    print("\n\nFOG check view created/updated: (Wall inside design option still need to be selected by excluding design option)")
    for type in selected_types:
        view_name = "EnneadTab FOG Check_" + type
        print("\t\t" + view_name)
        view = get_plan_view(view_name)
        __revit__.ActiveUIDocument.ActiveView = view

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":


    detect_FOG()
