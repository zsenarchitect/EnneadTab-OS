
__alias__ = "ToggleBlockColorDisplay"
__doc__ = "Toggle on/off for highlighting the different block type. Very helpful when you have many block variation."

import Rhino # pyright: ignore
import scriptcontext as sc
import rhinoscriptsyntax as rs
import random


from EnneadTab.RHINO import RHINO_CONDUIT
from EnneadTab import DATA_FILE
from EnneadTab import COLOR





def toggle_block_color_display():
    global COLOR_DICT
    COLOR_DICT = DATA_FILE.get_sticky_longterm("EA_COLOR_BLOCK_DICT", dict())

    conduit = None
    key = "EA_color_block_display_conduit"
    if sc.sticky.has_key(key):
        conduit = sc.sticky[key]
    else:
        # create a conduit and place it in sticky
        conduit = EA_Color_Block_Conduit()
        sc.sticky[key] = conduit

    # Toggle enabled state for conduit. Every time this script is
    # run, it will turn the conduit on and off
    conduit.Enabled = not conduit.Enabled
    if conduit.Enabled: print ("conduit enabled")
    else: print ("conduit disabled")
    sc.doc.Views.Redraw()
    rs.EnableRedraw(False)
    change_block_obj_display(conduit.Enabled)
    DATA_FILE.set_sticky_longterm("EA_COLOR_BLOCK_DICT", COLOR_DICT)
    print ("Tool Finished")


class EA_Color_Block_Conduit(RHINO_CONDUIT.RhinoConduit):
    def DrawForeground(self, e):
        text = "Ennead Color Block Mode"
        color = rs.CreateColor([87, 85, 83])
        #color = System.Drawing.Color.Red
        position_X_offset = 20
        position_Y_offset = 40
        size = 40
        bounds = e.Viewport.Bounds
        pt = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)
        e.Display.Draw2dText(text, color, pt, False, size)
        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 30)
        e.Display.Draw2dText("Left Click to toggle obj color refresh, Right click to toggle block names display", color, pt, False, 20)

        pt = Rhino.Geometry.Point2d(pt[0], pt[1] + 30)
        size = 15
        offset = 15

        key = "EA_color_block_display_conduit_show_text"
        if not sc.sticky.has_key(key):
            sc.sticky[key] = True
        if not sc.sticky[key]:
            return


        for blockname in rs.BlockNames(sort = True):
            count = rs.BlockInstanceCount(blockname)
            if count == 0:
                continue
            # visible_blocks = [rs.IsVisibleInView(x) for x in rs.BlockInstances(blockname)]
            # if len(visible_blocks) == 0 :
            #     continue
            pt = Rhino.Geometry.Point2d(pt[0], pt[1] + offset)
            color = get_color_from_blockname(blockname)
            # text = "{}: {} count".format(blockname, count)
            # if count > 1:
            #     text += "s"
            text = "{}: {} instances".format(blockname, count) if count > 1 else "{}: {} instance".format(blockname, count)
            e.Display.Draw2dText(text, color, pt, False, size)


        #print "Done"
        #True = text center around thge define pt, Flase = lower-left


def get_color_from_blockname(blockname):
    global COLOR_DICT
    if COLOR_DICT.has_key(blockname):
        red, green, blue = COLOR_DICT[blockname]
    else:
        red = int(255*random.random())
        green = int(255*random.random())
        blue = int(255*random.random())
        COLOR_DICT[blockname] = desaturate_color((red, green, blue))

    color = rs.CreateColor([red, green, blue])
    return color


def desaturate_color(color):
    normalized_color = (color[0]/256.0, color[1]/256.0, color[2]/256.0)
    hsv_color = COLOR.rgb_to_hsv(*normalized_color)
    grayed_hsv_color = (hsv_color[0], 0.6, hsv_color[2])
    grayed_rgb_color = COLOR.hsv_to_rgb(*grayed_hsv_color)
    denormalized_rgb_color = (int(grayed_rgb_color[0]*256), int(grayed_rgb_color[1]*256), int(grayed_rgb_color[2]*256))
    return color


def change_block_obj_display(is_apply_random_color):
    #print is_apply_random_color
    #print COLOR_DICT.values()

    def update_block_display(block_name):
        block_definition = sc.doc.InstanceDefinitions.Find(block_name)
        objs = block_definition.GetObjects()
        if is_apply_random_color:
            color = get_color_from_blockname(block_name)
            rs.ObjectColorSource(objs, source = 1)
            rs.ObjectColor(objs, color = color)
        else:
            rs.ObjectColorSource(objs, source = 0)


    block_names = rs.BlockNames(sort = True)
    map(update_block_display, block_names)