__title__ = "RandomizeBlockTransformation"
__doc__ = "Randomly transform block transformation for rotation and scale."

import rhinoscriptsyntax as rs
import random

from EnneadTab import DATA_FILE
from EnneadTab import SOUND

def randomize_block_transformation():
 

    ids = rs.GetObjects("Select block instances to rotate", filter = 4096, preselect=True)

    if not ids:
        return



    default_use_rotation = DATA_FILE.get_sticky_longterm("random_transform_rotation", True)
    default_use_scale_1d_soft = DATA_FILE.get_sticky_longterm("random_transform_scale_1d_soft", True)
    default_use_scale_1d_taller = DATA_FILE.get_sticky_longterm("random_transform_scale_1d_taller", False)
    default_use_scale_3d = DATA_FILE.get_sticky_longterm("random_transform_scale_3d", False)
    default_show_animation = DATA_FILE.get_sticky_longterm("random_transform_show_animation", False)

    option_list = [["Rotation", default_use_rotation],
                    ["Height scale 1D softly (0.9~1.1 factor)", default_use_scale_1d_soft],
                    ["Height scale 1D taller (1.4~1.7 factor)(override softer option if checked)", default_use_scale_1d_taller],
                    ["Scale 3D evenly (1.0~1.25)", default_use_scale_3d],
                    ["Animate process (Feel the zen of watching it go...)", default_show_animation]]
    res = rs.CheckListBox(items = option_list,
                            message= "select random options from below",
                            title="EnneadTab Random Transform")
    print (res)
    if not res: return
    for option, state in res:
        if option == option_list[0][0]:
            use_rotation = state
            continue
        if option == option_list[1][0]:
            use_1d_H = state
            continue
        if option == option_list[2][0]:
            use_1d_H_tall = state
            continue
        if option == option_list[3][0]:
            use_3d = state
            continue
        if option == option_list[4][0]:
            show_animation = state
            continue


    vec = rs.VectorCreate([0,0,1], [0,0,0])
    if not show_animation:
        rs.EnableRedraw(False)

    for i, id in enumerate(ids):
        if show_animation and i % 35 == 0:
            print (i)
            SOUND.play_sound(file = "sound effect_dice.wav")
        pt = rs.BlockInstanceInsertPoint(id)
        if use_rotation:
            ang = random.randrange(-180, 180)
            rs.RotateObject(id, pt,ang,vec)

        if use_1d_H:
            z_scale = random.uniform(0.9, 1.1)
        else:
            z_scale = 1.0


        if use_1d_H_tall:
            z_scale = random.uniform(1.4, 1.7)

        if use_3d:
            xyz_scale = random.uniform(1.0, 1.25)
        else:
            xyz_scale = 1.0

        if xyz_scale != 1.0:
            rs.ScaleObject(id, pt,[xyz_scale,xyz_scale,xyz_scale],False)

        if z_scale != 1.0:
            rs.ScaleObject(id, pt,[1,1,z_scale],False)


    # sc.sticky["random_transform_rotation"] = use_rotation
    DATA_FILE.set_sticky_longterm("random_transform_rotation", use_rotation)
    DATA_FILE.set_sticky_longterm("random_transform_scale_1d_soft", use_1d_H)
    DATA_FILE.set_sticky_longterm("random_transform_scale_1d_taller", use_1d_H_tall)
    DATA_FILE.set_sticky_longterm("random_transform_scale_3d", use_3d)
    DATA_FILE.set_sticky_longterm("random_transform_show_animation", show_animation)

    SOUND.play_sound(file = "sound effect_popup msg3.wav")
    SOUND.play_sound(file = "sound effect_dice.wav")


