#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from Autodesk.Revit import DB # pyright: ignore
except:
    pass

def project_pt_in_view(pt, view):
    """transfer a spatial point to flatten to the view Cplane

    Args:
        pt (DB.XYZ): _description_
        view (DB.View): _description_

    Returns:
        DB,XYZ: the flattern the spatial point in the view Cplane
    """
    z = view.ViewDirection
    origin = view.Origin

    project_vec = (pt - origin).DotProduct(z) * z
    return pt - project_vec


def project_crv_in_view(crv, view):
    """transfer a curve to view CPlane, 

    Args:
        crv (DB.Curve): the begining curve should be spatially parrelal to the view Cplane
        view (DB.View): _description_

    Returns:
        DB.Curve: the projected curve
    """


    pt0 = crv.GetEndPoint(0)
    pt1 = project_pt_in_view(pt0, view)

    vec = pt1 - pt0
    transform = DB.Transform.CreateTranslation (vec)
    return crv.CreateTransformed  (transform)

def project_crv_to_ground(crv):
    """project curve to ground

    Args:
        crv (DB.Curve): the begning curve should be parrallel to ground Cplane

    Returns:
        DB.Curve: _description_
    """
    if crv.IsCyclic:
        pt0 = crv.Evaluate(0, False)
    else:
        pt0 = crv.GetEndPoint(0)
    z = pt0.Z

    #print "original crv z = " + str(z)
    dist = abs(z)
    vec = DB.XYZ(0,0,-z)
    transform = DB.Transform.CreateTranslation (vec)
    return crv.CreateTransformed  (transform)



def get_intersect_pt_from_crvs(crv1, crv2, project_to_ground = True):
    """get the spatial intersection point between two curves

    Args:
        crv1 (DB.Curve): _description_
        crv2 (DB.Curve): _description_
        project_to_ground (bool, optional): If true, project to ground first before calcuting intersection. Defaults to True.

    Returns:
        DB.XYZ: the intersection point if any, return None if no intersection
    """
    import clr # pyright: ignore
    if project_to_ground:
        crv1 = project_crv_to_ground(crv1)
        crv2 = project_crv_to_ground(crv2)


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
            print ("%%%%many intersection")


        raw_pt = iResult.Item[0].XYZPoint
        if project_to_ground:
            projected_pt = DB.XYZ(raw_pt.X,raw_pt.Y,0)
            return projected_pt
        else:
            return raw_pt
    else:
        print(res)
    return None

def nearest_pt_from_pts(my_pt, pts):
    pts.sort(key = lambda x: my_pt.DistanceTo(x))
    return pts[0]



# https://mp.weixin.qq.com/s/h89ChVFg-mHM4NLStCjNuQ
# good ref on how to convert get revit geo




"""special thanks to https://danimosite.wordpress.com/2021/09/07/transforms-transformed/
for converting between inrernal and surbey/project point"""
def get_survey_transform(doc):
    # Gets the Active Project Locations (survey points) Transform. 
    return doc.ActiveProjectLocation.GetTotalTransform()
 


def get_project_transform(doc):
    # Get the Project Base Points Transform.
    project_location_info = get_project_location_info(doc)
     
    return project_location_info.GetTotalTransform()
 
def get_project_location_info(doc):
    # Get the Project Base Points Transform.
    project_location_info = next((l for l in DB.FilteredElementCollector(doc).OfClass(DB.ProjectLocation).WhereElementIsNotElementType().ToElements() if l.Name == "Project"), None)
    return project_location_info


def apply_inverse_transform(t, pt):
    # Applies the inverse transformation of the given Transform to the given point.
    return t.Inverse.OfPoint(pt)


def transform_internal_pt_to_project_coordinate(doc, pt):
    # Transforms the given point from the internal coordinate system to the project coordinate system.
    return apply_inverse_transform(get_project_transform(doc), pt)

def transform_internal_pt_to_survey_coordinate(doc, pt):
    # Transforms the given point from the project coordinate system to the internal coordinate system.
    return apply_inverse_transform(get_survey_transform(doc), pt)

def transform_project_pt_to_internal_pt(doc, pt):
    # Transforms the given point from the project coordinate system to the internal coordinate system.
    return get_project_transform(doc).OfPoint(pt)

def transform_survey_pt_to_internal_pt(doc, pt):
    # Transforms the given point from the project coordinate system to the internal coordinate system.
    return get_survey_transform(doc).OfPoint(pt)