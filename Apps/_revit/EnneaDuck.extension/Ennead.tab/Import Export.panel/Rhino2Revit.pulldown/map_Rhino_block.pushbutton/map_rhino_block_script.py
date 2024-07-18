#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Transform the Rhino block orientation to Adaptive Revit Family. \
It will be searching for same name as block name.\n The biggest benift is \
You will no longer be restricted by level based vertical up family. It can be \
freeform as in Rhino."
__title__ = "Map Rhino Block\nto Revit Family"
__youtube__ = "https://youtu.be/FMLv-_szLpM"
import math
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #


import proDUCKtion # pyright: ignore 
from EnneadTab import ERROR_HANDLE
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def get_type_by_name(name):
    types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsElementType().ToElements()

    def get_name(item):
        try:
            return item.Name
            #print "-name attr"
        except:
            return item.LookupParameter("Type Name").AsString()
            #print "-type name lookup"

    my_type = filter(lambda x: get_name(x) == name, types)
    if len(my_type) == 0:
        print("##Cannot find family type: " + name)
        return None
    return my_type[0]

def place_new_instance(type_name, transform, rotation_tuple, reflection):
    type = get_type_by_name(type_name)
    #frame = DB.Frame()
    #frame.Transform(combined_transform)
    #plane = DB.Plane.Create(frame)




    X = transform[0][-1]
    Y = transform[1][-1]
    Z = transform[2][-1]
    #print EA_UTILITY.internal_to_mm(Z)
    #temp_instance = doc.Create.NewFamilyInstance (DB.XYZ(X,Y,Z), type, DB.Structure .StructuralType.NonStructural) #--->use for conventional generic family
    temp_instance = DB.AdaptiveComponentInstanceUtils.CreateAdaptiveComponentInstance(doc, type)
    insert_pt = DB.AdaptiveComponentInstanceUtils.GetInstancePlacementPointElementRefIds(temp_instance)[0]





    """
    idea:
    place ADP instance at workd origin, get its transform, apply csv transform, set it back to instance
    AdaptiveComponentInstanceUtils(FamilyInstance famInst, Transform trf, bool unHost)
    """



    rotation = DB.Transform.CreateTranslation(DB.XYZ(0,0,0))# this is a empty move, just to create a transofmrm



    rotate_angle_x, rotate_angle_y, rotate_angle_z = rotation_tuple
    #print rotate_angle_x, rotate_angle_y, rotate_angle_z

    #print "###### new instance"
    axis = DB.XYZ(0,0,1)
    axis = rotation.BasisZ
    #print axis
    angle = rotate_angle_z
    pt = DB.XYZ(0, 0, 0)
    rotation = DB.Transform.CreateRotationAtPoint (axis, angle, pt) * rotation

    if reflection:
        """
        reflection = DB.Transform.CreateReflection (DB.Plane.CreateByThreePoints(DB.XYZ(0,0,0),
                                                                                DB.XYZ(0,1,0),
                                                                                DB.XYZ(0,0,1)))
        rotation = reflection
        """
        DB.AdaptiveComponentInstanceUtils.SetInstanceFlipped (temp_instance, True)
        rotation = DB.Transform.CreateRotationAtPoint (axis, math.pi, pt) * rotation


    #axis = DB.XYZ(0,1,0)
    #axis = rotation.OfVector(axis)
    #print axis
    axis = rotation.BasisY
    #print axis
    angle = rotate_angle_y
    pt = DB.XYZ(0, 0, 0)
    rotation = DB.Transform.CreateRotationAtPoint (axis, angle, pt) * rotation

    #axis = DB.XYZ(1,0,0)
    #axis = rotation.OfVector(axis)
    axis = rotation.BasisX
    angle = rotate_angle_x
    pt = DB.XYZ(0, 0, 0)
    rotation = DB.Transform.CreateRotationAtPoint (axis, angle, pt) * rotation






    #translation = DB.XYZ(X, Y, Z)

    #print rotation
    #DB.AdaptiveComponentInstanceUtils.MoveAdaptiveComponentInstance (temp_instance , rotation, True)

    #DB.ElementTransformUtils(doc, temp_instance.Id, translation)
    #temp_instance = doc.Create.NewFamilyInstance(face, insert_pt, local_x_axis, type)

    #translation = DB.Transform.CreateTranslation(DB.XYZ(X, Y, Z + EA_UTILITY.mm_to_internal(21800)))
    translation = DB.Transform.CreateTranslation(DB.XYZ(X, Y, Z))
    #print X, Y, Z
    #print translation
    total_transform = translation * rotation
    DB.AdaptiveComponentInstanceUtils.MoveAdaptiveComponentInstance (temp_instance , total_transform, True)


    actual_Z = doc.GetElement(DB.AdaptiveComponentInstanceUtils.GetInstancePlacementPointElementRefIds(temp_instance)[0]).Position.Z
    #print EA_UTILITY.internal_to_mm(actual_Z)
    #return
    z_diff = Z - actual_Z
    #print z_diff
    #translation = DB.Transform.CreateTranslation(DB.XYZ(0, 0, EA_UTILITY.mm_to_internal(21800)))
    additional_translation = DB.Transform.CreateTranslation(DB.XYZ(0, 0, z_diff))
    total_transform = additional_translation * total_transform
    DB.AdaptiveComponentInstanceUtils.MoveAdaptiveComponentInstance (temp_instance , total_transform, True)

def read_data(data):
    block_name = data.split(",", 1)[0][2:-1]
    #print block_name


    transform_string_and_ZYZ_string_and_reflection_string = data.split(",", 1)[1]
    transform_string_and_ZYZ_string = transform_string_and_ZYZ_string_and_reflection_string[0:-4]
    reflection_string = transform_string_and_ZYZ_string_and_reflection_string[-2:-1]
    #print transform_string_and_ZYZ_string
    ZYZ_string = transform_string_and_ZYZ_string.split("], ")[1]
    #print ZYZ_string
    rotation_tuple = ZYZ_string.strip("()").split(",")
    #print rotation_tuple
    rotation_tuple = (float(x) for x in rotation_tuple)

    transform_string = transform_string_and_ZYZ_string.split("], ")[0][2:-1]
    #print transform_string
    #print transform_string
    transform = []

    for i, item in enumerate(transform_string.split(",")):

        if i % 4 == 0:
            temp = []
        temp.append(EA_UTILITY.mm_to_internal(float(item.replace("(","").replace(")",""))))
        if i % 4 == 3:
            transform.append(temp)
    #print "*******"
    #print transform


    #print transform
    #print rotation_tuple
    reflection = True if reflection_string == "1" else False
    return block_name, transform, rotation_tuple, reflection

def map_block():
    file_path = EA_UTILITY.get_filepath_in_special_folder_in_EA_setting("Local Copy Dump", "map_block_transform.txt")

    raw_data = EA_UTILITY.read_txt_as_list(file_path)
    #for data in raw_data[0:10]:
    for data in raw_data:
        #print "###########"
        #print data
        block_name, transform, rotation_tuple, reflection = read_data(data)

        place_new_instance(block_name, transform, rotation_tuple, reflection)

    
@ERROR_HANDLE.try_catch_error()
def main():
    t = DB.Transaction(doc, "map blocks")
    t.Start()
    map_block()
    t.Commit()

################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    main()
    