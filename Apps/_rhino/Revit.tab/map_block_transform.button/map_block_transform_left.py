
__title__ = "MapBlockTransform"
__doc__ = "Send the transformation of the blocks to Revit to be used by space adaptive family. This is the only known way of doing true free 3D orientation in Revit."

import rhinoscriptsyntax as rs
import Rhino # pyright: ignore

import clr # pyright: ignore
import math


from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab import FOLDER, NOTIFICATION, DATA_FILE
"""
use Transform.DecomposeAffine Method (Vector3d, Transform, Transform, Vector3d) to decompose trnasform to trnaltion and rotation
for rotation, use Transform.GetEulerZYZ to get rotation angle of X,Y,Z axis(use radiun here)
then record rotation
"""

def get_data(block):
    def detail_matrix(xform):
        OUT = []
        for i in range(4):
            
            OUT.append( (xform[i,0], xform[i,1], xform[i,2], xform[i,3]) )
        return OUT

    block_name = rs.BlockInstanceName(block)

    transform = rs.BlockInstanceXform(block)

    
    translation = clr.StrongBox[Rhino.Geometry.Vector3d](Rhino.Geometry.Vector3d(0,0,0))
    rotation = clr.StrongBox[Rhino.Geometry.Transform](rs.XformIdentity())
    othor = clr.StrongBox[Rhino.Geometry.Transform](rs.XformIdentity())
    diagono = clr.StrongBox[Rhino.Geometry.Vector3d](Rhino.Geometry.Vector3d(0,0,0))
    transform.DecomposeAffine(translation, rotation, othor, diagono )
    
    print (transform.IsSimilarity (0.001))
    similarity = transform.IsSimilarity (0.001)
    if str(similarity) == "OrientationReversing":
        is_reflection = 1
    elif str(similarity) == "OrientationPreserving":
        is_reflection = 0
    else:
        is_reflection = 0

    angle_x = clr.StrongBox[float](0.0)
    angle_y = clr.StrongBox[float](0.0)
    angle_z = clr.StrongBox[float](0.0)

    rotation.GetYawPitchRoll (angle_z, angle_y, angle_x)
    



    rotate_tuple = (float(angle_x), 
                    float(angle_y),
                    float(angle_z))

    OUT = (block_name, detail_matrix(transform), rotate_tuple, is_reflection)
    print (OUT)
    
    return str(OUT)



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def map_block_transform():
    blocks = rs.GetObjects(message = "pick blocks", custom_filter = rs.filter.instance)
    data = [get_data(x) for x in blocks]
    rs.EnableRedraw(False)
    filepath = NOTIFICATION.DUMP_FOLDER + "\map_block_transform.txt"
    DATA_FILE.set_list(data, filepath)
    NOTIFICATION.messenger(main_text = "map ready!")


if __name__ == "__main__":
    map_block_transform()