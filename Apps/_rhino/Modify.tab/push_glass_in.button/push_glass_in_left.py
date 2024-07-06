
__alias__ = "PushGlassIn"
__doc__ = "Make pushed in glass recess from selected srfs."
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

from Duckitect import COLOR

def push_glass_in():

    srf = rs.GetObjects("pick surfaces", rs.filter.surface)
    if not srf:
        return
    dist = rs.RealBox("How far to push in?", default_number=1)

    plural = "s" if len(srf) > 1 else ""
    opts = ["Delete input surface{}".format(plural), "Keep input surface{}".format(plural)]
    delete_input_res = rs.ListBox(opts, "What do you want to do with the input surface{}?".format(plural), default=opts[0])
    if delete_input_res == opts[0]:
        delete_input = True
    elif delete_input_res == opts[1]:
        delete_input = False
    else:
        return
        
    rs.EnableRedraw(False)
    [process_srf(srf, dist, delete_input) for srf in srf]






def process_srf(srf, dist, delete_input):
    layer = rs.ObjectLayer(srf)
    ring_layer = "{}::Reveal Return Face".format(layer)
    if not rs.IsLayer(ring_layer):
        rs.AddLayer(ring_layer)
        
        inverted_color = COLOR.invert_color(rs.LayerColor(layer))
        rs.LayerColor(ring_layer, inverted_color)
        
        
    brep_in = rs.coercebrep(srf)

    #rs.OffsetSurface()
    tolerance = sc.doc.ModelAbsoluteTolerance
    solid = Rhino.Geometry.Brep.CreateFromOffsetFace(brep_in.Faces[0], -dist, True, False, tolerance)
    
    copy = solid.DuplicateBrep()
    inset = copy.Faces.ExtractFace (0)
    inset_srf = sc.doc.Objects.AddBrep(inset)
    rs.ObjectLayer(inset_srf, layer)
    
    solid.Faces.RemoveAt(0)
    solid.Faces.RemoveAt(0)
    ring_srf = sc.doc.Objects.AddBrep(solid)
    rs.ObjectLayer(ring_srf, ring_layer)
    if delete_input:
        rs.DeleteObject(srf)
    
