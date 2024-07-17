
__title__ = "SectionboxByBoundingBox"
__doc__ = "Similar to Revit SectionBox, this will crop the view to just around the selected elements region. In Rhino display mode all clipper is supported. In Enscape only one of the clipper will be recognized."

import rhinoscriptsyntax as rs

from EnneadTab import NOTIFICATION
from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_OBJ_DATA
import section_box_right as SB
import section_box_utility


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def section_box():
    #NOTIFICATION.messenger(main_text = "Select the objs to do sectionbox boundingbox around")
    objs = rs.GetObjects(message = "Get objs to do sectionbox", filter = 0, group = True, preselect = True)
    rs.EnableRedraw(False)
    if objs is None:
        NOTIFICATION.messenger(main_text = "You didn't select anything.", sub_text = "Boundingbox cannot generate around emptyness...")
        return

    bbox_pts = rs.BoundingBox(objs, view_or_plane = rs.CurrentView(return_name = False))
    try:
        base_srf = rs.AddSrfPt([bbox_pts[0],bbox_pts[1],bbox_pts[2],bbox_pts[3]])
        crv = rs.AddLine(bbox_pts[0],bbox_pts[4])
        bbox = rs.ExtrudeSurface(base_srf, crv)
        #rs.DeleteObjects(bbox_pts)
        rs.DeleteObjects( [crv, base_srf])
    except Exception as e:
        NOTIFICATION.messenger(main_text = "Cannot find valid boundingbox", sub_text = "Might be a 1D or 2D element in current CPlane.")
        if "crv" in locals():
            try:
                rs.DeleteObject( crv )
            except Exception as e:
                print(e)
        if "base_srf" in locals():
            try:
                rs.DeleteObject( base_srf )
            except Exception as e:
                print(e)
        return

    scale = 1.2
    """
    for obj in objs:
        rs.MessageBox( rs.ObjectName(obj) == SB.GROUP_NAME_KEYWORD + "edges")
    """
    if all(rs.ObjectName(x) == section_box_utility.GROUP_NAME_KEYWORD + "edges" for x in objs):
        scale = 1.0#>>>>>>>>>>>>>>>>>to update, if user pick the dash bounding box, then dont need to scale up
    scale = [scale, scale, scale]

    """future try BoundingBox.Inflate Method (Double)
    Inflates the box with equal amounts in all directions. Inflating with negative amounts may result in decreasing boxes."""
    bbox = rs.ScaleObject(bbox, RHINO_OBJ_DATA.get_center(bbox), scale)
    print(bbox)

    SB.section_box(section_box_utility.GROUP_NAME_KEYWORD, predefined_polysurf = bbox)






if __name__ == "__main__":
    section_box()