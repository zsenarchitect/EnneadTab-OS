
__title__ = "FloorDrafter"
__doc__ = "This button does FloorDrafter when left click"

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc


from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab import SOUND, FOLDER, DATA_FILE


def process_brep(brep):
    print(brep)
    brep = sc.doc.Objects.Find(brep).Geometry
    print(brep)
    faces = brep.Faces
    print(brep.Edges)
    out = dict()
    for i, face in enumerate(faces):
        print(face)
        """

        edge_loop = face.OuterLoop
        edge_crv = edge_loop.To3dCurve()
        """
        """
        extrac_face = faces.ExtractFace(i)
        extrac_face.Vertices
        """
        temp_brep = face.DuplicateFace (False)
       

        tol = sc.doc.ModelAbsoluteTolerance
        ang_tol = sc.doc.ModelAngleToleranceRadians

        joined_crvs = Rhino.Geometry.Curve.JoinCurves( temp_brep.Edges, tol)
        
        ##### this skipp any hole it might have
        outter_crv = sorted(joined_crvs, key = lambda x: x.GetLength())[-1]



        pts = outter_crv.Simplify (Rhino.Geometry.CurveSimplifyOptions.All, tol, ang_tol).ToNurbsCurve ().GrevillePoints()

        # pts = temp_brep.Vertices
        for pt in pts:
            print(pt)
        out[i] = [[x[0], x[1], x[2]] for x in pts]
        continue
    
    return out
    """
    face_id = face.SurfaceIndex
    surf = brep.Faces.ExtractFace(face_id)

    edge_ids = face.AdjacentEdges()
    print(edge_ids)
    edges = [brep.Edges[x].EdgeCurve for x in list(edge_ids)]
    print(edges)

    tolerance = sc.doc.ModelAbsoluteTolerance
    joined_crvs = Rhino.Geometry.Curve.JoinCurves(edges, tolerance)
    print(joined_crvs)
    """


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def floor_drafter():
    breps = rs.GetObjects("Select object to export")
    if not breps:
        return
    
    rs.EnableRedraw(False)

    def good_brep(id):
        if rs.ObjectType(id) == 8:
            return True
        if rs.ObjectType(id) == 16:
            return True
        return False
        
    breps = filter(good_brep, breps)

    out = dict()
    for brep in breps:
        data = process_brep(brep)
        if data:
            out[brep.ToString()] = data
    

    file = FOLDER.get_EA_dump_folder_file("BREP2FLOOR_DATA.json")
    DATA_FILE.save_dict_to_json(out, file)

    SOUND.play_sound("sound effect_mario message.wav")




if __name__ == "__main__":
    floor_drafter()