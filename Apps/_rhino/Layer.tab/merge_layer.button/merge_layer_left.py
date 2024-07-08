__title__ = "MergeLayer"
__doc__ = "Merge multiple layer to single layer. This process include merging layers owned by blocks."

import rhinoscriptsyntax as rs
import scriptcontext as sc

from EnneadTab.RHINO import RHINO_FORMS, RHINO_LAYER
from EnneadTab import NOTIFICATION
from EnneadTab import SOUNDS


def merge_layer():

    all_layers = rs.LayerNames()
    all_layers_user = [RHINO_LAYER.rhino_layer_to_user_layer(x) for x in all_layers]
    """
    print(all_layers[10])
    temp = rhino_layer_to_user_layer(all_layers[10])
    print(temp)
    print(user_layer_to_rhino_layer(temp))
    """


    layers_to_modify, layer_target = RHINO_FORMS.select_from_list2list(all_layers_user,
                                                                        all_layers_user,
                                                                        title = "EnneadTab Merge Layer",
                                                                        message = "Select Layers to modify, hold 'shift' to select multiple. Blocks process included.",
                                                                        search_A_text = "Source Layers(Multiple)",
                                                                        search_B_text = "Target Layer(Single) as one to keep",
                                                                        multi_select_A = True,
                                                                        multi_select_B = False,
                                                                        button_names = ["Merge"],
                                                                        width = 600,
                                                                        height = 500)





    if not layers_to_modify or not layer_target:
        NOTIFICATION.toast(main_text = "Cannot deal with empty selection.")
        return

    rs.EnableRedraw(False)
    layers_to_modify = [RHINO_LAYER.user_layer_to_rhino_layer(x) for x in layers_to_modify]
    layers_to_modify.sort(reverse = True)
    layer_target = RHINO_LAYER.user_layer_to_rhino_layer(layer_target)
    # print layers_to_modify
    # print layer_target
    #print_list(layers_to_modify)

    block_names = rs.BlockNames(sort = True)



    try:
        map(lambda x: modify_block(x,layers_to_modify, layer_target), block_names)
        map(lambda x: modify_obj_on_layer(x, layer_target), layers_to_modify)
        map(lambda x: rs.DeleteLayer(x), layers_to_modify)
        temp = ""
        for x in layers_to_modify:
            temp += "{}\n".format(RHINO_LAYER.rhino_layer_to_user_layer(x))
        display = "Layers below have been merged to {}\n\n{}".format(RHINO_LAYER.rhino_layer_to_user_layer(layer_target), temp)
        rs.MessageBox(message = display, buttons= 0 | 48, title = "Done")
    except Exception as e:
        display = "Sometime merging parent layer while containing child can raise error saying some of the child layer structure cannot be found. This is becasue thier parent have changed name.\n\nThe best way to avoid this is to start merging from the inner side and moveup the hierarchy one parent at a time.\n\n(If the error message below DOES NOT sound like the description above, please report to SenZhang, you might have discovered a bug. Thank you in advance!)\n\nError Message Below:\n\n" + str(e)
        rs.MessageBox(message = display, buttons= 0 | 48, title = "Too aggresive merging...")


    SOUNDS.play_sound(file = "sound effect_popup msg3.wav")


def modify_obj_on_layer(current_layer, layer_target):

    objs =  rs.ObjectsByLayer(current_layer)
    rs.ObjectLayer(objs, layer_target)



def modify_block(block_name, layers_to_modify, layer_target):
    # print block_name
    block_definition = sc.doc.InstanceDefinitions.Find(block_name)
    objs = block_definition.GetObjects()
    geos = []
    attrs = []
    for i , obj in enumerate(objs):
        geos.append(obj.Geometry)
        attrs.append(obj.Attributes)
        current_layer = rs.ObjectLayer(obj)
        if current_layer in layers_to_modify:
            rs.ObjectLayer(obj, layer_target)

    # print geos
    # print attrs
    return


def print_list(list):
    temp = ""
    for x in list:
        temp += str(x) + "\n"
    rs.TextOut(message = temp)