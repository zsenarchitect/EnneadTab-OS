#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Adjust fin height by intersecting detail line."
__title__ = "92_adjust_fin"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def process_ball(ball, guide_crv):
    print("$$$$$$$$$$$$")
    location = ball.Location.Point
    #print location
    location = EnneadTab.REVIT.REVIT_GEOMETRY.project_pt_in_view(location, doc.ActiveView)
    #print location
    pt0 = DB.XYZ(location.X, location.Y, 0)
    pt1 = DB.XYZ(location.X, location.Y, 200)
    search_beam = DB.Line.CreateBound(pt0, pt1)

    Xpt = EnneadTab.REVIT.REVIT_GEOMETRY.get_intersect_pt_from_crvs(search_beam, guide_crv, project_to_ground = False)
    if not Xpt:
        return

    #print Xpt

    h_diff = Xpt.Z - location.Z
    h_diff = EnneadTab.REVIT.REVIT_UNIT.internal_to_mm(h_diff)
    h_diff = round(h_diff/10)*10
    print(h_diff)
    if abs(h_diff) > 15000:
        return
    if abs(h_diff) < 5:
        return
    h_diff = EnneadTab.REVIT.REVIT_UNIT.mm_to_internal(h_diff)
    #return
    panel = ball.SuperComponent
    current_h = panel.LookupParameter("thick pier H").AsDouble()
    new_h = current_h + h_diff
    panel.LookupParameter("thick pier H").Set(new_h)



def adjust_fin():
    uidoc = __revit__.ActiveUIDocument
    selection_ids = uidoc.Selection.GetElementIds ()
    if len(selection_ids) == 0:
        selection = uidoc.Selection.PickObjects(UI.Selection.ObjectType.Subelement, "Pick diagram curve")
        selection = [doc.GetElement(x) for x in selection]
        print(selection)
    else:
        selection = [doc.GetElement(x) for x in selection_ids]

    def is_ok_crv(x):
        if type(x) == DB.DetailCurve:
            return True
        if type(x) == DB.DetailNurbSpline :
            return True
        if type(x) == DB.DetailArc :
            return True
        if type(x) == DB.DetailLine:
            return True

        return False

    guide_crv = filter(is_ok_crv, selection)
    if len(guide_crv) != 1:
        print("Pick just one guide curve")
        return

    guide_crv = guide_crv[0].GeometryCurve
    guide_crv = EnneadTab.REVIT.REVIT_GEOMETRY.project_crv_in_view(guide_crv, doc.ActiveView)




    #get all position family in view.
    all_GMs = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    balls = filter(lambda x: x.Symbol.Family.Name == "location point", all_GMs)
    if len(balls) == 0:
        return


    #process each dot
    t = DB.Transaction(doc, __title__)
    t.Start()
    #$$$$$$$$$$$$$$$$$$$
    map(lambda x: process_ball(x, guide_crv), balls)
    t.Commit()

    print("\n\n\nAll finished")

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    adjust_fin()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)










