#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT
import ENVIRONMENT

if ENVIRONMENT.is_Rhino_environment():
    import rhinoscriptsyntax as rs
    import scriptcontext as sc


def sort_pts_by_Z(pts):
    pts = sorted(pts, key=lambda x: x.Z)
    return pts

def sort_pts_along_crv(pts, crv):
    
    pts = sorted(pts, key=lambda x: rs.CurveClosestPoint(crv, x))
    return pts

def sort_AB_along_crv(pt0, pt1, crv):
    """return pt0 and pt1 that 0<1. This also handle closedCrv where seam is between the two pts."""
    t0 = rs.CurveClosestPoint(crv,pt0)
    t1 = rs.CurveClosestPoint(crv,pt1)
    t0 = rs.CurveNormalizedParameter(crv, t0)
    t1 = rs.CurveNormalizedParameter(crv, t1)


    if t1 < t0:
        t0, t1 = t1, t0
        pt0, pt1 = pt1, pt0

    if not rs.IsCurveClosed(crv):
        return pt0, pt1

    if abs(t1 - t0) > abs(t0) + abs(1-t1):
        pt0, pt1 = pt1, pt0

    return pt0, pt1



def get_center(obj):
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    center = (min + max)/2
    return center

def get_obj_h(obj):
    corners = rs.BoundingBox(obj)
    min = corners[0]
    max = corners[6]
    z_diff = (max.Z - min.Z)
    return z_diff

def get_boundingbox_edge_length(obj):
    corners = rs.BoundingBox(obj)
    X = rs.Distance(corners[0], corners[1])
    Y = rs.Distance(corners[1], corners[2])
    Z = rs.Distance(corners[0], corners[5])
    return X, Y, Z


def get_obj_min_center_pt(obj):
    pts = rs.BoundingBox(obj)
    pt0 = pts[0]
    pt1 = pts[2]
    return (pt0 + pt1)/2


def get_instance_geo(block_instance):
    """get the instance geometry from instance id.
    You cannot directly get the geometry from the instance refernce object becasue there is nothing there.

    Args:
        block_instance (guid): _description_

    Returns:
        all geos of the instance(list of Rhino.Geometry): _description_
    """

    
    
    
    block_name = rs.BlockInstanceName(block_instance)
    # contents = [sc.doc.Objects.Find(x).Geometry for x in rs.BlockObjects(block_name)]
    

    non_block_objs, block_instance_objs = [], []


    for x in rs.BlockObjects(block_name):
        (block_instance_objs if rs.IsBlockInstance(x) else non_block_objs).append(x)
        
    non_block_geos = [sc.doc.Objects.Find(x).Geometry for x in non_block_objs]
    # print non_block_geos
    # print block_instance_objs
    block_geos = []
    for x in block_instance_objs:
        block_geos.extend(get_instance_geo(x))
    geo_contents = non_block_geos + block_geos
    
    transform = rs.BlockInstanceXform(block_instance)

    [x.Transform(transform) for x in geo_contents]
    return geo_contents

