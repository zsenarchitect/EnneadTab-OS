
__title__ = "ImportSelectedMaterial"
__doc__ = "Import selected materials from a file."

import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino # pyright: ignore

from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_FORMS




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def import_selected_material():


    filename = rs.OpenFileName(title = "pick a Rhino file to import view from",
                                filter = "Rhino 3D Models (*.3dm)|*.3dm||")
    if not filename:
        return

    f = Rhino.FileIO.File3dm.Read(filename)
    if (f.AllMaterials.Count == 0):
        print ("no material in this file")
        return

    print (f.AllMaterials)
    availible_materials = [[x.Name, False] for x in f.AllMaterials]
    print (availible_materials)
    
    availible_materials.sort(key = lambda x: x[0].lower())

    print (availible_materials)


    picked_material_name = RHINO_FORMS.select_from_list(availible_materials,
                                                    title = "EnneadTab material importer",
                                                    message = "select materials to import from [{}]".format(filename),
                                                    multi_select = True,
                                                    button_names = ["Select Multiple Materials"],
                                                    width = 500,
                                                    height = 500)


    if not picked_material_name:
        return



    for source_material in f.AllMaterials:

        if material.Name in picked_material_name:
            """
            sphere = Rhino.Geometry.Sphere(Rhino.Geometry.Plane.WorldXY, 500)
            id = sc.doc.Objects.AddSphere(sphere)
            obj = sc.doc.Objects.FindId(id)
            obj.RenderMaterial = material
            """
            
            #rs.MatchMaterial(source_material.Id
            #source_material.Name = "temp_" + source_material.Name
            material = Rhino.Render.RenderMaterial.CreateBasicMaterial(source_material, sc.doc)
            sc.doc.RenderMaterials.Add(material)
            return



if __name__ == "__main__":
    import_selected_material()