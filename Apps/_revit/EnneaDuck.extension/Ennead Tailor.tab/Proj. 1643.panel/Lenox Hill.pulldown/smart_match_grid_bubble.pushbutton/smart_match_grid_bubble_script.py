#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """This use the grphaical extend setup on all main LifeSafety view as guide to set all plan view grid visual. 

It is the best invention since ketchup."""
__title__ = "Smart Match Grid Graphic"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 
import time
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

REF_VIEWS = {
    "B2":"LS-001_10_B2",
    "B1":"LS-002_10_B1",
    "L1":"LS-003_10_L1",
    "L2":"LS-004_10_L2",
    "L3":"LS-005_10_L3",
    "L4":"LS-006_10_L4",
    "L5":"LS-007_10_L5",
    "L6":"LS-008_10_L6",
    "L7":"LS-009_10_L7",
    "L8":"LS-010_10_L8",
    "L9":"LS-011_10_L9",
    "L10":"LS-012_10_L10",
    "L10 MEZZ":"LS-013_10_L10 MEZZ",
    "L11":"LS-014_10_L11",
    "L12":"LS-015_10_L12",
    "L13":"LS-016_10_L13",
    "L14":"LS-017_10_L14",
    "L15":"LS-018_10_L15",
    "L16":"LS-019_10_L16",
    "L17":"LS-020_10_L17",
    "L18":"LS-021_10_L18",
    "L19":"LS-022_10_L19",
    "L20":"LS-023_10_L20",
    "L21 MEP":"LS-024_10_L21 MEP",
    "L22 MEP":"LS-025_10_L22 MEP"
}



def set_base_leaders():
    leader_record = {}
    for view in [REVIT_VIEW.get_view_by_name(x) for x in REF_VIEWS.values()]:
        all_grids = DB.FilteredElementCollector(doc, view.Id).OfClass(DB.Grid).WhereElementIsNotElementType().ToElements()

        for grid in all_grids:
            for grid_end in [DB.DatumEnds.End0, DB.DatumEnds.End1]:

                try:
                    key = "{}_{}".format(grid.Id.IntegerValue, grid_end)
                    if key in leader_record:
                        # reuse existing leader setting.
                        current_leader = grid.GetLeader (grid_end, view)
                        if not current_leader:
                            grid.AddLeader (grid_end, view)
                        if grid.IsLeaderValid  (grid_end, view, leader_record[key]):
                            grid.SetLeader (grid_end, view, leader_record[key] )
                        else:
                            print ("Leader not valid: {}, {}, {}".format(output.linkify(view.Id, title=view.Name), grid.Name, grid_end))
                    else:
                        #first time encountering, no need to change graphic, just record leader
                        leader = grid.GetLeader (grid_end, view)
                        if leader:
                            leader_record[key] = leader
                except:
                    print ("Give up: {}, {}, {}".format(output.linkify(view.Id, title=view.Name), grid.Name, grid_end))
                    
    return True


@ERROR_HANDLE.try_catch_error
def smart_match_grid_bubble():
    # get all floor plans and area plans
    # for each view, find all grids. Then for each end of 
    # the grid decide if it should show bubble or not based 
    # on the status of same bubble from same level in REF dict.

    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    # set_base_leaders()
    # t.Commit()
    # return



    
    all_plans = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    all_plans = [x for x in all_plans if x.ViewType in [DB.ViewType.FloorPlan, DB.ViewType.AreaPlan]]
    all_plans = [x for x in all_plans if x.Name not in REF_VIEWS.values()]
    all_plans = [x for x in all_plans if not x.IsTemplate ]
    all_plans.sort(key = lambda x: x.Name)
    # all_plans = [x for x in all_plans if x.Name.startswith("TEST_")]

    ref_views_resolved = {k: REVIT_VIEW.get_view_by_name(v) for k, v in REF_VIEWS.items()}

    for view in all_plans:
        start_time = time.time()
        all_grids = DB.FilteredElementCollector(doc, view.Id).OfClass(DB.Grid).WhereElementIsNotElementType().ToElements()
        if not all_grids:
            continue

        level_name = view.GenLevel.Name
        if level_name not in REF_VIEWS:
            continue

        print ("\nWorking on {}".format(output.linkify(view.Id, title=view.Name)))
        for grid in all_grids:
            for grid_end in [DB.DatumEnds.End0, DB.DatumEnds.End1]:
                try:
                    is_show_bubble = grid.IsBubbleVisibleInView(grid_end, ref_views_resolved[level_name])
                    if is_show_bubble:
                        grid.ShowBubbleInView(grid_end, view)
                    else:
                        grid.HideBubbleInView(grid_end, view)




                    extent_type = grid.GetDatumExtentTypeInView  (grid_end, ref_views_resolved[level_name])
                    curves = grid.GetCurvesInView (extent_type, ref_views_resolved[level_name])
                    grid.SetDatumExtentType (grid_end, view, extent_type)
                    grid.SetCurveInView (extent_type, view, curves[0])

                    

                    leader = grid.GetLeader (grid_end, ref_views_resolved[level_name])
                    if leader and grid.IsLeaderValid  (grid_end, view, leader):
                        current_leader = grid.GetLeader (grid_end, view)
                        if not current_leader:
                            grid.AddLeader (grid_end, view)
                        grid.SetLeader (grid_end, view, leader )
                    
                        
                except Exception as e:
                    print ("Skip <{}> in <{}> becasue {}".format(grid.Name, output.linkify(view.Id, title=view.Name), e))

        end_time = time.time()
        print ("Done in {} seconds".format(end_time - start_time))
                

    t.Commit()
    print ("\n\n\n\n\n\nFinished")
    NOTIFICATION.messenger("Done!")

################## main code below #####################

if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    smart_match_grid_bubble()
    ENNEAD_LOG.use_enneadtab(coin_change=20, tool_used=__title__.replace("\n", " "), show_toast=True)
