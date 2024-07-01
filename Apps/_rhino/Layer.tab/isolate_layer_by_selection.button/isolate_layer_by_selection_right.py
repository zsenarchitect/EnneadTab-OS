
__alias__ = "SelectObjectsOnSimilarLayer"
__doc__ = "This button does SelectObjsOnSimilarLayer when right click"

import rhinoscriptsyntax as rs


def isolate_layer_by_selection():
    ids = rs.SelectedObjects(include_lights = True, include_grips = False)
    if not ids: return
    rs.EnableRedraw(False)
    used_layers = set()
    obj_by_layers = []
    for id in ids:
        layer = rs.ObjectLayer(id)
        used_layers.add(layer)

    for layer in list(used_layers):
        obj_by_layers.extend(rs.ObjectsByLayer(layer, True))

