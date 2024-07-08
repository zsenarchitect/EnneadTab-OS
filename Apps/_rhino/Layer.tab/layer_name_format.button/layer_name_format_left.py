
__title__ = "LayerNameFormat"
__doc__ = "Format the spelling of layer name on selected layers."


import rhinoscriptsyntax as rs
import scriptcontext as sc

from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_LAYER

IGNORE_PATTERN = [r"\[GFA\]"]

#  key = possible wrong format after renamer,
# value = correct format that should alwasy rollback to
# RECOVER_DICT = {"[gfa]": "[GFA]",
#                 "[seat_crvs]":"[SEAT_CRVS]",
#                 "ea_seating_bake": "EA_Seating_Bake",
#                 "ea seating bake": "EA_Seating_Bake",
#                 "Ea Seating Bake": "EA_Seating_Bake",
#                 "EA SEATING BAKE": "EA_Seating_Bake",
#                 "EA_SEATING_BAKE": "EA_Seating_Bake"}

RECOVER_DICT = dict()
PROTECTED_NAMES = ["[GFA]",
                   "[SEAT_CRVS]",
                   "EA_Seating_Bake",
                   "EA_Facade Mapping_[Active]",
                   "EA_Facade Mapping_",
                   "design_geos",
                   "source_srf", 
                    "ref_srf",
                    "Mapped_Facade",
                    "Mapped_Facade_"]
for name in PROTECTED_NAMES:
    RECOVER_DICT[name.title()] = name
    RECOVER_DICT[name.upper()] = name   
    RECOVER_DICT[name.lower()] = name
    RECOVER_DICT[name.title().replace(" ", "_")] = name
    RECOVER_DICT[name.upper().replace(" ", "_")] = name   
    RECOVER_DICT[name.lower().replace(" ", "_")] = name 
    RECOVER_DICT[name.title().replace("_", " ")] = name
    RECOVER_DICT[name.upper().replace("_", " ")] = name   
    RECOVER_DICT[name.lower().replace("_", " ")] = name 


# for key,value in sorted(RECOVER_DICT.items(), key=lambda tuple: (tuple[0].upper(), tuple[0][0].islower())):
#     print "{} -> {}".format(key, value)
    


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def layer_name_format():
    selected_layers = RHINO_LAYER.get_layers(message = "Select layers you want to modify.")


    mentioned_names = []
    for full_layer in selected_layers:
        mentioned_names.extend( full_layer.split("::"))

    
    opts = ["Using Title Case", 
            "using lower case", 
            "USING FULL CASE", 
            "replace_all_space_with_underline",
            "replace all underscore with space"]

    res = rs.PopupMenu(opts)
    # print res
    if  res is None:
        return
    
            
            
    for layer in sc.doc.Layers:
        if should_ignore(layer) or layer.Name is None:
            continue
 

        
        if layer.Name not in mentioned_names:
            continue
        
    
        if res == 0:
            new_name = layer.Name.title()
        elif res == 1:
            new_name = layer.Name.lower()
        elif res == 2:
            new_name = layer.Name.upper()
        elif res == 3:
            new_name = layer.Name.replace(" ", "_")
        elif res == 4:
            new_name = layer.Name.replace("_", " ")
        else:
            continue
        
        for checker in RECOVER_DICT:
            if checker in new_name:
                new_name = new_name.replace(checker, RECOVER_DICT[checker])
        
        print ("{} ->{}".format(layer.Name, new_name))
        layer.Name = new_name
    

def should_ignore(layer):
    return False


if __name__ == "__main__":
    layer_name_format()