
__title__ = "DestroyLayer"
__doc__ = "Delete selected layers, even if there are objs in it. Helpful when layer tree is constrainted by block usage."

import rhinoscriptsyntax as rs
import scriptcontext as sc
from EnneadTab.RHINO import RHINO_LAYER

def destroy_layer():
    layers = RHINO_LAYER.get_layers(message="What layers to destory?")  
    if not layers: return

    for layer in layers:
        print (layer)
        print (rs.IsLayer(layer))
        rs.PurgeLayer(layer)




