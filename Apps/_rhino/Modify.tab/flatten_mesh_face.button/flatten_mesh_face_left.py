
__title__ = "FlattenMeshFace"
__doc__ = "This button does FlattenMeshFace when left click"

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
from EnneadTab import LOG, ERROR_HANDLE

def highlight_planar_region(mesh):
    dot_name = "EA_mesh_flat_face_marker"
    dots = rs.ObjectsByName(dot_name)
    #rs.DeleteObjects(dots)
    tolerance = sc.doc.ModelAbsoluteTolerance
    for i, face in enumerate(mesh.Faces):
        if face.IsTriangle:
            dot = rs.AddTextDot("flat", mesh.Faces.GetFaceCenter(i))
            rs.ObjectName(dot, name = dot_name)
            continue

        face_corners = [face.A, face.B, face.C, face.D]
        face_corners = [Rhino.Geometry.Point3d(mesh.Vertices[x]) for x in face_corners]
        #print face_corners

        face_corners = EnneadTab.DATA_CONVERSION.list_to_system_list(face_corners, type = Rhino.Geometry.Point3d)
        test_crv = Rhino.Geometry.PolylineCurve(face_corners)

        if test_crv.IsPlanar(tolerance):
            print("is flat face")
            dot = rs.AddTextDot("flat", mesh.Faces.GetFaceCenter(i))
            rs.ObjectName(dot, name = dot_name)


    dots = rs.ObjectsByName(dot_name)
    rs.AddObjectsToGroup(dots, rs.AddGroup())


def process_mesh(mesh):
    # all_face normals(not normals, that is for the vertice)
    # all topologyvetivecs


    topo_vertice = mesh.TopologyVertices

    new_topo_vertice_new_locations = [process_vertex(index, vertex, mesh) for index, vertex in enumerate(topo_vertice)]
    for index, topo_vertex in enumerate(topo_vertice):
        mesh_vertex_ids = topo_vertice.MeshVertexIndices (index)
        for mesh_vertex_id in mesh_vertex_ids:
            mesh.Vertices .SetVertex(mesh_vertex_id, new_topo_vertice_new_locations[index])
    return mesh

def process_vertex(index, vertex, mesh):
    #print index
    # each topovertex get connected face index
    connected_face_indexs = mesh.TopologyVertices.ConnectedFaces(index)
    #print list(connected_face_indexs)
    #connected_faces = [original_mesh.Faces[x] for x in connected_face_indexs]


    # use the face index to get the facenormal around each topovertice
    face_normals = mesh.FaceNormals
    face_normals.ComputeFaceNormals ()

    connected_face_normals = [face_normals[x] for x in connected_face_indexs]


    # get the face centroid, and use face normal to create a plane to get projection of top vertivce.Later should add weight to the strength.
    connected_face_centers = [mesh.Faces.GetFaceCenter(x) for x in connected_face_indexs]

    temp_planes = [Rhino.Geometry.Plane(center, normal) for center, normal in zip(connected_face_centers,connected_face_normals)]
    #print temp_planes


    # move topo vertice to new location.
    vec = Rhino.Geometry.Vector3d(0,0,0)
    for plane in temp_planes:
        project_pt = plane.ClosestPoint(vertex)

        project_pt = Rhino.Geometry.Point3d(project_pt)
        #print type(project_pt)
        vertex = Rhino.Geometry.Point3d(vertex)

        #print type(vertex
        raw_vec = Rhino.Geometry.Vector3d(project_pt - vertex)
        if raw_vec.Length < 1:
            factor = 1
        else:
            factor = 0.5
        vec += raw_vec * factor
    final_pt = vertex + vec
    return final_pt




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def flatten_mesh_face():
    #   get the mesh
    """
    current_selection = rs.SelectedObjects()
    if len(current_selection) == 0:
        return
        mesh_id = rs.ObjectsByType(32)[0]# 32 is mesh
    elif len(current_selection) > 1:

        return
    """
    mesh_id = rs.GetObject(message = "Pick one mesh to flatten", filter = 32, preselect = True)
    if not mesh_id:
        return
    mesh_obj = sc.doc.Objects.FindId(mesh_id)
    mesh = mesh_obj.Geometry
    obj_attribute = mesh_obj.Attributes
    #print mesh

    for x in dir(mesh):
        #print x
        pass

    step = 0
    mesh_obj = None

    while step < 500:

        mesh = process_mesh(mesh)
        print("######### Steps {}#####".format(step + 1))
        if mesh_obj:
            rs.DeleteObject(mesh_obj)
        mesh_obj = sc.doc.Objects.AddMesh(mesh, obj_attribute )
        rs.Redraw()
        step += 1

        if step % 100:
            highlight_planar_region(mesh)

if __name__ == "__main__":
    flatten_mesh_face()