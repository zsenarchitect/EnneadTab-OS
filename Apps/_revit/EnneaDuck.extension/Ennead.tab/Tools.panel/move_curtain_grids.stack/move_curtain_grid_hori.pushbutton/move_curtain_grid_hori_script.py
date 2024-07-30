#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Move the horitiontal curtain grids on a curtain wall to nearest intersecting Detail Lines/Levels.\n\nDo this on elevation view."
__title__ = "Align H. Curtain Grid To Detail Lines/Levels(Elevation)"
__youtube__ = "https://youtu.be/iiAy-Gxl5ZU"
__tip__ = True
# from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE
from EnneadTab import NOTIFICATION

from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore
import clr
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

def project_crv(crv):

    pt0 = crv.GetEndPoint(0)
    z = pt0.Z

    #print "original crv z = " + str(z)
    dist = abs(z)
    vec = DB.XYZ(0,0,-z)
    transform = DB.Transform.CreateTranslation (vec)
    return crv.CreateTransformed  (transform)




def get_intersect_pt_from_crvs(crv1, crv2):
    crv1 = project_crv(crv1)
    crv2 = project_crv(crv2)


    #print "after crv1 z = " + str(crv1.GetEndPoint(0).Z)
    #print "after crv2 z = " + str(crv2.GetEndPoint(0).Z)

    res = crv1.Intersect(crv2)
    #print res
    if res == DB.SetComparisonResult.Overlap:

        #iResult = DB.IntersectionResultArray()
        iResult = clr.StrongBox[DB.IntersectionResultArray](DB.IntersectionResultArray())
        #iResult = StrongBox[resultArray](DB.IntersectionResultArray())
        crv1.Intersect(crv2,iResult)
        if iResult.Size > 1:
            print("%%%%many intersection")


        raw_pt = iResult.Item[0].XYZPoint
        projected_pt = DB.XYZ(raw_pt.X,raw_pt.Y,0)
        return projected_pt
    return None

def nearest_Z_from_zList(my_Z, zList):
    zList.sort(key = lambda x: abs(my_Z - x))
    return zList[0]


def process_wall(wall, crvs):
    print("Processing wall: {}".format(output.linkify(wall.Id)))

    intersect_pts_Z = []

    for crv in crvs:

        if isinstance(crv, DB.Level):
            #print crv.Elevation
            #print crv.ProjectElevation
            intersect_pts_Z.append(crv.ProjectElevation )
            """
            options = DB.Options()
            options.View = doc.ActiveView
            abstract_crv = crv.Geometry[options]
            print(abstract_crv)
            """



        if isinstance(crv, DB.DetailLine ):
            abstract_crv = crv.GeometryCurve
            #print abstract_crv.GetEndPoint(0).Z
            intersect_pts_Z.append(abstract_crv.GetEndPoint(0).Z)

    all_grid_zList = [doc.GetElement(x).FullCurve.GetEndPoint(0).Z for x in wall.CurtainGrid.GetUGridLineIds ()]
    all_grid_zList.sort()
    #print intersect_pts_Z
    #intersect_pts_Z.append(all_grid_zList[0])
    #intersect_pts_Z.append(all_grid_zList[-1])
    #print intersect_pts_Z


    for grid in [doc.GetElement(x) for x in wall.CurtainGrid.GetUGridLineIds ()]:
        #print "{}".format(output.linkify(grid.Id))
        #print grid.FullCurve
        pt_Z = grid.FullCurve .GetEndPoint(0).Z

        target_pt_Z = nearest_Z_from_zList(pt_Z, intersect_pts_Z)

        vecter = DB.XYZ(0,0,target_pt_Z - pt_Z)
        #line = DB.Line.CreateBound(target_pt, projected_pt)
        #doc.Create.NewDetailCurve(doc.ActiveView, line)
        #print vecter
        #DB.Transform.CreateTranslation (vecter)
        DB.ElementTransformUtils.MoveElement(doc, grid.Id,vecter)

@ERROR_HANDLE.try_catch_error()
def move_curtain_grid():

    walls = uidoc.Selection.PickObjects(UI.Selection.ObjectType.Element, "Pick walls")
    walls = [doc.GetElement(x) for x in walls]
    walls = filter(lambda x: isinstance(x, DB.Wall), walls)
    if len(walls) == 0:
        NOTIFICATION.messenger("No walls selected.")
        return

    try:
        crvs = uidoc.Selection.PickObjects(UI.Selection.ObjectType.Subelement, "Pick detail crvs or levels that will intersect your wall")
    except:
        NOTIFICATION.messenger("NO intersection content picked.")
        return
    if len(crvs) == 0:
        NOTIFICATION.messenger("No detail crvs or levels selected.")
        return

    crvs = [doc.GetElement(x) for x in crvs]



    t = DB.Transaction(doc, __title__)
    t.Start()

    map(lambda x: process_wall(x, crvs), walls)
    t.Commit()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    move_curtain_grid()
    
