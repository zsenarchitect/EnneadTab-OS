
__alias__ = "UniformTransformBlocks"
__doc__ = "Apply same rotational transformation for the blocks. Helpful when you have to reorient many directional blocks, such as changing the direction of cars on street."


import rhinoscriptsyntax as rs

def uniform_transform_blocks():
    ids = rs.GetObjects("Select block instances to rotate", filter = 4096, preselect=True)

    if not ids:
        return





    option_list = ["Rotation"]
    value_list = [180]
    res = rs.PropertyListBox(option_list,
                            value_list,
                            message= "How much angle to rotate each block around insert point?",
                            title="EnneadTab Uniformly Transform")

    if res is None:
        return

    if ids is None: return
    vec = rs.VectorCreate([0,0,1], [0,0,0])
        
    rs.EnableRedraw(False)

    for i, id in enumerate(ids):

        pt = rs.BlockInstanceInsertPoint(id)

        ang = float(res[0])
        rs.RotateObject(id, pt,ang,vec)


