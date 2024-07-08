
__title__ = "FallGeosOnGeo"
__doc__ = "Drop selected objs to a receiver geo. If it is block, drop using the insertion point. Otherwise using the center of buttom face of the boundingbox."

import rhinoscriptsyntax as rs
from EnneadTab.RHINO import RHINO_OBJ_DATA

def fall_geos_on_geo():
    
    # get the blocks
    #blocks = rs.GetObjects("Pick blocks to project.", rs.filter.instance)
    objs = rs.GetObjects("Pick objs to project.")
    if not objs:
        return

    # get surf or poly surf, 8 and 16 are internal defined object type enum
    landing_geo = rs.GetObject("Pick surface or polysurface to fall onto.", filter = 8 + 16)
    if not landing_geo:
        return

    # disable viewport refreshing to save time.
    rs.EnableRedraw(False)


    # process each block from the block selection
    map(lambda x: process_obj(x, landing_geo), objs)

def process_obj(obj, landing_geo):

    # get block point insertion
    if rs.IsBlockInstance(obj):
        pt = rs.BlockInstanceInsertPoint(obj)
    else:
        pt = RHINO_OBJ_DATA.get_obj_min_center_pt(obj)
        


    # get project to landing_geo pt
    try:
        #proejct block pt to the geometry
        project_pts = list(rs.ProjectPointToSurface(pt, landing_geo, (0,0,-1)))

        # sort result intersection pts by Z value from highest to lowest
        project_pts.sort(key = lambda x: x[2], reverse = True)

        # only get the highest pt
        project_pt = project_pts[0]
    except Exception as e:
        print (e)
        print ("Cannot project this block over. Skipping.")
        # terminate this action early.
        return

    # move block over
    vector = project_pt - pt
    rs.MoveObject(obj, vector)