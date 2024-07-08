
__title__ = "InitiateLayers"
__doc__ = "Initiate layer tree for quick start on programing or facade design."

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino # pyright: ignore


from EnneadTab import COLOR

LAYER_COLOR_MAP_BY_MATERIAL = {
    "Glass": (162, 195, 208),
    "Metal": (195, 162, 208),
    "Mullion": (182, 189, 186),
    "Shadowbox Backpan": (121, 146, 167)
}

LAYER_COLOR_MAP_BY_NAME = {
    "Office": (156, 211, 223),
    "Retail": (241, 226, 142),
    "MEP": (176, 176, 176),
    "Resi": (226, 89, 49),
    "Lab": (150, 120, 120)
}



def initiate_layers():
    options = ["Facade Layer Scheme", "Program Blocks Layer Scheme"]
    new_layer_scheme_options = rs.ListBox(items = options,
                                    message= "select layer scheme option from below",
                                    title = "New Layer Scheme")
    if new_layer_scheme_options == options[0]:
        parent_layer = "EA_Facade"
        scheme_layer_options = LAYER_COLOR_MAP_BY_MATERIAL
    elif new_layer_scheme_options == options[1]:
        parent_layer = "EA_Program"
        scheme_layer_options = LAYER_COLOR_MAP_BY_NAME
    else:
        return

    options = [[key, True] for key in scheme_layer_options]
    res = rs.CheckListBox(items = options, 
                          message = "select sublayers for '{}'".format(parent_layer), 
                          title = "Initiating Layer Structure")
    print (res)

    for option, state in res:
        if not state:
            continue

        for layer_name, color in scheme_layer_options.items():

            if option != layer_name:
                continue
            
            full_layer_name = "{}::{}".format(parent_layer, layer_name)
            rs.AddLayer(name = full_layer_name,
                        color = get_color(color),
                        parent = None)

            continue



def has_any_keyword(input, keywords):
    for keyword in keywords:
        if keyword in input.lower():
            return True
    return False


def get_color(tuple):
    red, green, blue = tuple
    return COLOR.from_rgb(red,green,blue)