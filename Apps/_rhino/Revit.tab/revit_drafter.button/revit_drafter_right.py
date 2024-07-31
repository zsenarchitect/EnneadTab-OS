
__title__ = "RevitDrafterExport"
__doc__ = "Send the draft content back to Revit."
import rhinoscriptsyntax as rs

from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab import ENVIRONMENT, NOTIFICATION, DATA_FILE
from EnneadTab.RHINO import RHINO_LAYER

def get_final_children_layer_name(layer_name):
    #layer_name = rs.LayerName(obj)
    if "OUT" in layer_name:
        return layer_name.split("OUT::")[-1]
    if "::" in layer_name:
        return layer_name.split("::")[-1]
    return layer_name

def pt_to_tuple(pt):
    return (pt.X, pt.Y, pt.Z)


def get_data_from_line( crv):
    """data
    layer name,
    object type(line, arc, surface),
    geo_tuple: if line: (pt0, pt1), if arc, (startpt, midpt, endpt), if surface, (list of line in loop, diretion sequnced)

    """
    out = dict()
    pts = (pt_to_tuple(rs.CurveStartPoint(crv)),
            pt_to_tuple(rs.CurveEndPoint(crv)))
    out["construct_info"] = pts
    out["type"] = "line"
    return out


def get_data_from_arc(crv):
    out = dict()
    pts = (pt_to_tuple(rs.CurveStartPoint(crv)),
            pt_to_tuple(rs.ArcMidPoint(crv)),
            pt_to_tuple(rs.CurveEndPoint(crv)))
    out["type"] = "arc"
    out["construct_info"] = pts
    return out


def get_data_from_circle(crv):
    out = dict()
    pts = (pt_to_tuple(rs.CircleCenterPoint(crv)), rs.CircleRadius(crv))
    out["type"] = "circle"
    out["construct_info"] = pts

    return out


def get_data_from_ellipse(crv):
    out = dict()
    pts = (rs.EllipseCenterPoint(crv), rs.EllipseQuadPoints(crv))
    out["type"] = "ellipse"
    out["construct_info"] = pts

    return out


def get_data_from_nurbs_crv(crv):
    out = dict()
    pts = rs.CurvePoints(crv)
    pts = tuple(pt_to_tuple(x) for x in pts)
    out["type"] = "nurbs_crv"
    out["construct_info"] = pts

    return out


def get_datas_from_crvs( crvs):
    trash_objs = rs.ExplodeCurves(crvs, delete_input = False)
    #print [rs.ObjectType(x) for x in trash_objs]


    # for each segement.
    # get data:
    data = []
    for obj in trash_objs:
        obj_id = obj.ToString()
        #print obj_id
        if rs.IsLine(obj):
            data.append( get_data_from_line(obj))
            continue

        if rs.IsArc(obj):
            data.append( get_data_from_arc(obj))
            continue

        if rs.IsCircle(obj):
            data.append( get_data_from_circle(obj))
            continue

        if rs.IsEllipse(obj):
            data.append( get_data_from_ellipse(obj))
            continue

        data.append( get_data_from_nurbs_crv(obj))

    rs.DeleteObjects(trash_objs)
    return data

def get_datas_from_srf( srfs):
    data = []
    for srf in srfs:
        borders = rs.DuplicateSurfaceBorder(srf)
        #print borders
        temp = []
        for border in borders:
            border_data = get_datas_from_crvs(border)
            rs.DeleteObjects(border)
            temp.append(border_data)
        srf_data = dict()
        srf_data["type"] = "srf"
        srf_data["construct_info"] = temp
        obj_id = srf.ToString()
        data.append( srf_data)

    return data


def validate_layer_objs(out_layers):

    for layer in out_layers:
        if "Curves" in layer:
            objs = rs.ObjectsByLayer(layer)
            for obj in objs:
                if rs.ObjectType(obj) != 4:
                    return layer
        if "FilledRegion" in layer:
            objs = rs.ObjectsByLayer(layer)
            for obj in objs:
                if rs.ObjectType(obj) != 8:
                    return layer





def process_layer(layer):

    # get objs in out layers, filter only lines, arc,  polyline, polyarc, polycurve
    objs = rs.ObjectsByLayer(layer)
    objs = filter(lambda x: not rs.IsObjectHidden(x), objs)

    if "Curves" in layer:
        data = get_datas_from_crvs(objs)
    if "FilledRegion" in layer:
        data = get_datas_from_srf(objs)


    return data




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def revit_drafter():

    # get all layers related to OUT
    all_layers = rs.LayerNames()
    def include_OUT(x):
        parent_layer = rs.ParentLayer(x)
        if parent_layer is None or "OUT" not in rs.ParentLayer(x):
            return False
        return True
    out_layers = filter(include_OUT, all_layers)

    bad_layer = validate_layer_objs(out_layers)
    if bad_layer:
        NOTIFICATION.messenger(main_text = "Please only put crvs on curve layer, and surface on filledregion layer.", sub_text = RHINO_LAYER.rhino_layer_to_user_layer(bad_layer))
        return


    # collection data from each layer
    OUT_Data = dict()

    for layer in out_layers:
        layer_data = process_layer(layer)
        if not layer_data:
            continue
        OUT_Data[layer] = layer_data

    """
    OUT_Data[layerA] = layer_data(dict of contents)

    layer_data[id] = obj_dict(dict of data)

    obj_dict[type] = line/arc/circle/nurbs/srf
    obj_dict[construct_info] = (pt0, pt1)/(pt0, pt1, pt2)/(pt0, r)/obj_dict_of_border_crv
    """

    print ("final data")
    """
    for key, value in OUT_Data.items():
        print("##")
        print(key)
        print(value)
    """

    #print OUT_Data
    DATA_FILE.pretty_print_dict(OUT_Data)

    # save data to dump folder\
    DATA_FILE.set_data(OUT_Data, "EA_DRAFTING_TRANSFER.sexyDuck")

    NOTIFICATION.messenger(main_text = "Draft Data recorded. You can return to Revit now")



if __name__ == "__main__":
    revit_drafter()