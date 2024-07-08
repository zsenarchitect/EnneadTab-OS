#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT
import ENVIRONMENT
if ENVIRONMENT.is_Rhino_environment():
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs
    import scriptcontext as sc



def get_material_by_name(name, return_index = False):
    mats = sc.doc.Materials
    """
    print("searching material with name: " + name)
    for mat in mats:
        print(mat.Name)
    """

    mat = filter(lambda x: x.Name == name, mats)
    if len(mat) != 0:
        if return_index:
            return mat[0].MaterialIndex
        else:
            return mat[0]
    return None


def create_material(name, RGBAR, return_index = False):
    # RGBAR = (r,g,b,t,R)
    from System.Drawing import Color
    import Rhino # pyright: ignore
    material = Rhino.DocObjects.Material()
    material.Name = name
    material = Rhino.Render.RenderMaterial.CreateBasicMaterial(material, sc.doc)
    sc.doc.RenderMaterials.Add(material)


    sphere = Rhino.Geometry.Sphere(Rhino.Geometry.Plane.WorldXY, 500)
    id = sc.doc.Objects.AddSphere(sphere)
    obj = sc.doc.Objects.FindId(id)
    obj.RenderMaterial = material
    obj.CommitChanges()

    material = get_material_by_name(name)
    if material is None:
        rs.TextOut(message = "No material named [{}] found after creating material, contact Sen for help on why.".format(name), title = "EnneadTab")
    #material.CommitChanges()
    #print "begin changing material = {}".format(material)
    red, green, blue, transparency, reflectivity = RGBAR # trnasparency 0 = solid, 1 = see-thru,,,,,reflectivity 0 = matte, 255 = glossy
    material.DiffuseColor = Color.FromArgb(red,green,blue)
    #print material.DiffuseColor
    material.Transparency = transparency
    material.TransparentColor = Color.FromArgb(red,green,blue)
    #print material.TransparentColor
    material.ReflectionColor = Color.FromArgb(red,green,blue)
    material.Reflectivity = reflectivity
    material.ReflectionGlossiness = reflectivity
    material.Shine = reflectivity
    material.SpecularColor = Color.FromArgb(red,green,blue)
    material.AmbientColor  = Color.FromArgb(red,green,blue)

    material.CommitChanges()
    #rs.DeleteObject(id)
    if return_index:
        return material.MaterialIndex, id
    else:
        return material, id#return the sample material ball so the material is visible to search. you can delete ball with this ID after script.



def create_material_by_type(name,
                            RGBAR,
                            transparency_color = None,
                            type = 0,
                            return_index = True):
    """
    base_color_rgb ----> tuple of 3 int
    type = 0 --->basic
           1 --->glass
           2 --->metal
           3 --->plastic
           4 --->emission
           5 --->paint
           6 --->plaster
           10 ---> physically based

    trnasparency 0 = solid, 1 = see-thru
    reflectivity 0 = matte, 255 = glossy
    return material index by default, otherwise return material
    """

    import Rhino # pyright: ignore
    import scriptcontext as sc
    red, green, blue, transparency, reflectivity = RGBAR

    """
    bmtex = Rhino.Render.RenderContentType.NewContentFromTypeId(Rhino.Render.ContentUuids.BitmapTextureType)
    bmtex.Filename = "C:\\Users\\Nathan\\Pictures\\uvtester.png"

    simtex = bmtex.SimulatedTexture(Rhino.Render.RenderTexture.TextureGeneration.Allow)
    """
    #
    #print(Rhino.Render.ContentUuids.PhysicallyBasedMaterialType)
    #print(Rhino.Render.ContentUuids.GlassMaterialType)

    def create_physical_based_mat():
        # first create an empty PBR material
        pbr_rm = Rhino.Render.RenderContentType.NewContentFromTypeId(Rhino.Render.ContentUuids.PhysicallyBasedMaterialType)

        # to get to a Rhino.DocObjects.PhysicallyBasedMaterial we need to simulate the
        # render material first.
        sim = pbr_rm.SimulatedMaterial(Rhino.Render.RenderTexture.TextureGeneration.Allow)

        # from the simulated material we can get the Rhino.DocObjects.PhysicallyBasedMaterial
        pbr = sim.PhysicallyBased

        # now we have an instance of a type that has all the API you need to set the PBR
        # properties. For simple glass we set color to white, opacity to 0 and opacity
        # IOR to 1.52
        pbr.Opacity = 0.0
        pbr.OpacityIOR = 1.52
        pbr.BaseColor = Rhino.Display.Color4f.White

        pbr.SetTexture(simtex.Texture(), Rhino.DocObjects.TextureType.PBR_BaseColor)

        # convert it back to RenderMaterial
        new_pbr = Rhino.Render.RenderMaterial.FromMaterial(pbr.Material, sc.doc)
        # Set a good name
        new_pbr.Name = name

        # Set pbr ui sections visible
        """
        new_pbr.SetParameter("pbr-show-ui-basic-metalrough", True);
        new_pbr.SetParameter("pbr-show-ui-subsurface", True);
        new_pbr.SetParameter("pbr-show-ui-specularity", True);
        new_pbr.SetParameter("pbr-show-ui-anisotropy", True);
        new_pbr.SetParameter("pbr-show-ui-sheen", True);
        new_pbr.SetParameter("pbr-show-ui-clearcoat", True);
        new_pbr.SetParameter("pbr-show-ui-opacity", True);
        new_pbr.SetParameter("pbr-show-ui-emission", True);
        new_pbr.SetParameter("pbr-show-ui-bump-displacement", True);
        new_pbr.SetParameter("pbr-show-ui-ambient-occlusion", True);
        """

        return new_pbr

    if type == 10:
        mat = create_physical_based_mat()


    # Add it to the document
    sc.doc.RenderMaterials.Add(mat)
    if return_index:
        return get_material_index(mat)##material name might surfix number if similar name exist, so the index should be get from final product not name.
    else:
        return mat
