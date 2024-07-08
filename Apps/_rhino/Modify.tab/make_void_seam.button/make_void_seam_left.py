
__title__ = "MakeVoidSeam"
__doc__ = "Make the void cut polysurface based on layer name."


import rhinoscriptsyntax as rs
import re

from EnneadTab.RHINO import RHINO_LAYER


def make_void_seam():
    
    # get layer, msg note = pick the layer that contains seam location guide. layer name format: seam_large[20]
    layers = RHINO_LAYER.get_layers(message = "Pick the layer(s) that contains seam location guide.\nLayer name format:\n\tdescription[rhino unit for seam width]\nexample:\n\tseam_large[20]")

    if not layers:
        return

    # check dist if valid
    if not all([get_width_from_layer_name(x) for x in layers]):
        return

    rs.EnableRedraw(False)

    map(process_layer, layers)


def get_width_from_layer_name(layer_name):
    if "::" in layer_name:
        layer_name = layer_name.split("::")[-1]
    try:
        """
        >>> import re
        >>> s = u'abcde(date=\'2/xc2/xb2\',time=\'/case/test.png\')'
        >>> re.search(r'\((.*?)\)',s).group(1)
        u"date='2/xc2/xb2',time='/case/test.png'"
        s = r"seam[12]"
        print(s)
        print(re.search(r"\[(.*?)\]", s).group(1))
        """
        width = float(re.search(r"\[(.*?)\]", layer_name).group(1))
        return width
    except Exception as e:
        rs.MessageBox("Cannot get width data from layer name: " + layer_name)
        print(e)
        return None


def process_layer(layer_name):
    # get lines in layer
    lines = rs.ObjectsByLayer(layer_name)#later add filter to get lines only, no polycurve

    width = get_width_from_layer_name(layer_name)
    OUT = []

    # process each line
    for line in lines:
        copy_line = rs.CopyObject(line, [0,0,0])

        # extend line longer
        rs.ExtendCurveLength(copy_line, extension_type = 2, side = 2, length = rs.CurveLength(line) * 0.1)

        # offset line half dist each way
        offset_1 = rs.OffsetCurve(copy_line, direction = [1, 1, 1], distance = width/2, normal = None, style = 1)
        offset_2 = rs.OffsetCurve(copy_line, direction = [1, 1, 1], distance = -width/2, normal = None, style = 1)

        # extrude up and down the dist of length---------------->> maybe just call offset srface command
        srf = rs.AddLoftSrf([offset_1, offset_2])

        z = rs.CurveLength(line) * 2#later change it normal of the loft plane
        crv = rs.AddLine([0, 0, 0], [0, 0, z])#later change it normal of the loft plane
        polysrf = rs.ExtrudeSurface(srf, crv, cap = True)
        rs.MoveObject(polysrf, [0, 0, - z  *0.5])
        OUT.append(polysrf)
        rs.DeleteObjects([srf, crv, offset_1, offset_2, copy_line])


    # group outcome
    rs.AddObjectsToGroup(OUT, rs.AddGroup())
    void_layer_name = layer_name + "_Voids"
    rs.ObjectLayer(OUT, layer = RHINO_LAYER.secure_layer(void_layer_name))
    rs.LayerColor(void_layer_name, color = rs.LayerColor(layer_name))

    pass
