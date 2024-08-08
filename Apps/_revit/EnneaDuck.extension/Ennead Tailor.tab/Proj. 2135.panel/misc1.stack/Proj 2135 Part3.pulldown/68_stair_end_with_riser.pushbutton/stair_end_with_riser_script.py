#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Check if the stairs are ending with a riser."
__title__ = "68_stair_end_with_riser(Checker)"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
#from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def stair_end_with_riser():


    report()
    #fix()

def fix():
    # get selection
    pass


def report():
    t = DB.Transaction(doc, "create stair check view")
    t.Start()
    view = make_3D_views_contain_only_stair()
    t.Commit()
    __revit__.ActiveUIDocument.ActiveView = view

    t = DB.Transaction(doc, "check stair riser condition")
    t.Start()
    stairs = DB.FilteredElementCollector(doc).OfClass(DB.Architecture.Stairs).WhereElementIsNotElementType().ToElements()
    for stair in stairs:
        view.SetElementOverrides(stair.Id, DB.OverrideGraphicSettings() )
        output_flag = False
        run_ids = stair.GetStairsRuns ()
        for run_id in run_ids:
            run = doc.GetElement(run_id)
            if not run.EndsWithRiser:
                #print "Run is not ending with riser"
                output_flag = True
        if output_flag:
            setting = DB.OverrideGraphicSettings()
            setting.SetSurfaceForegroundPatternColor(DB.Color(255,0,0))
            setting.SetSurfaceForegroundPatternId(EnneadTab.REVIT.REVIT_SELECTION.get_solid_fill_pattern_id(doc))
            view.SetElementOverrides(stair.Id, setting )

            stair_type = doc.GetElement(stair.GetTypeId()).LookupParameter("Type Name").AsString()
            try:
                level_start = doc.GetElement(stair.LookupParameter("Base Level").AsElementId()).Name
            except:
                level_start = "???"
            try:
                level_end = doc.GetElement(stair.LookupParameter("Top Level").AsElementId()).Name
            except:
                level_end = "???"
            addition_note = ""

            if stair.GroupId.IntegerValue  > 0:
                addition_note = " [Contained in a group.]"
            output.print_md("Stair [{}], ***{}*** to ***{}***, Stair has run is not ending with riser.**{}**---->{}".format(stair_type,
                                                                                                                level_start,
                                                                                                                level_end,
                                                                                                                addition_note,
                                                                                                                output.linkify(stair.Id, title = "Select stair")))
            run_ids = stair.GetStairsRuns ()
            for run_id in run_ids:
                run = doc.GetElement(run_id)
                if not run.EndsWithRiser:
                    print("\t\t{} Run is not ending with riser---->{}".format(addition_note, output.linkify(run.Id, title = "Select run")))


    t.Commit()
    print("\n\n Tool finished. Run it again after modifying stairs to keep checking.")



def make_3D_views_contain_only_stair():


    view = create_view("EnneadTab Stair Riser Check View")
    for cate in doc.Settings.Categories:
        if not view.CanCategoryBeHidden( cate.Id):
            continue
        if cate.Name != "Stairs":
            view.SetCategoryHidden(cate.Id, True)
        else:
            view.SetCategoryHidden(cate.Id, False)

    try:
        view.LookupParameter("Views_$Group").Set("00_EA's_Little Helper")
        view.LookupParameter("Views_$Series").Set("Stair Check")
    except:
        pass

    return view

def create_view(view_name):
    desired_name = view_name
    view = get_view_by_name(desired_name)
    if view is not None:
        return view
    print("####creating new axon view for " + view_name)

    view = DB.View3D.CreateIsometric (doc, get_threeD_view_type().Id)
    view.Name = desired_name

    return view

def get_view_by_name(name):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    for view in all_views:
        if name == view.Name:
            return view
    return None

def get_threeD_view_type():
    view_family_types = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()
    return filter(lambda x: x.ViewFamily == DB.ViewFamily.ThreeDimensional, view_family_types)[0]
################## main code below #####################
output = script.get_output()
output.close_others()
output.set_width(1000)


if __name__ == "__main__":

    stair_end_with_riser()
