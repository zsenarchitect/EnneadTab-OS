
__title__ = "IsolateLayerBySelection"
__doc__ = "Isolcate objs from similar layers"
import rhinoscriptsyntax as rs
from EnneadTab import LOG, ERROR_HANDLE, NOTIFICATION


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def isolate_layer_by_selection():
    ids = rs.GetObjects(message="Pick objs: ", preselect=True)
    if not ids: 
        NOTIFICATION.messenger("Nothing selected")
        return
    rs.EnableRedraw(False)

    used_layers = set()
    obj_by_layers = []
    for id in ids:
        layer = rs.ObjectLayer(id)
        used_layers.add(layer)

    for layer in list(used_layers):
        obj_by_layers.extend(rs.ObjectsByLayer(layer, True))

    invert_objs = rs.InvertSelectedObjects(include_lights = True)
    rs.HideObjects(invert_objs)


    rs.UnselectObjects(obj_by_layers)


if __name__ == "__main__":
    isolate_layer_by_selection()