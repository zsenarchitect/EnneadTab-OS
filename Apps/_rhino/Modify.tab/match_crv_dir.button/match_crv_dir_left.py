
__title__ = "MatchCrvDir"
__doc__ = "Match multiple crvs direction."

import rhinoscriptsyntax as rs
from EnneadTab import NOTIFICATION
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def match_crv_dir():
    base_crvs = rs.GetObjects(message = "pick many base curves", custom_filter = rs.filter.curve)
    """
    srfs = rs.AddPlanarSrf(base_crvs)
    rs.DeleteObjects(base_crvs)
    map(rs.DuplicateSurfaceBorder, srfs)
    rs.DeleteObjects(srfs)

    return
    """
    if not base_crvs:
        NOTIFICATION.messenger("No base curves founds.")
        return

    #good_crv = rs.GetObject(message = "pick one crv that has intended directions", custom_filter = rs.filter.curve)
    for base_crv in base_crvs:
        srf = rs.AddPlanarSrf(base_crv)
        x, y, z = rs.SurfaceNormal(srf, [0,0])
        
        if z < 0:
        #if not rs.CurveDirectionsMatch(good_crv, base_crv):
            print ("bad")
            print (rs.ReverseCurve(base_crv))
            
        else:
            print ("good")
        rs.DeleteObject(srf)


if __name__ == "__main__":
    match_crv_dir() 