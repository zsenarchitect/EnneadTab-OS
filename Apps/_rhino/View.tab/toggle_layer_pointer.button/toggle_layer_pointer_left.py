
__title__ = "ToggleLayerPointer"
__doc__ = "Short list layers with objs that is visible on screen. This is a good way to quickly examine the layer structure in your model space."

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System # pyright: ignore
from EnneadTab.RHINO import RHINO_OBJ_DATA, RHINO_LAYER, RHINO_CONDUIT

KEY = "EA_LAYERS_DISPLAY_Conduit"


class LayerDisplayConduit(RHINO_CONDUIT.RhinoConduit):

    @RHINO_CONDUIT.try_catch_conduit_error
    def DrawForeground(self, e):
        self.display_text(e,
                        text = "Ennead Visible Layer Mode",
                        size = RHINO_CONDUIT.ConduitTextSize.Title)

        self.display_text(e,
                        text = "Short list layers with objs that is visible on screen.",
                        size = RHINO_CONDUIT.ConduitTextSize.Normal)
        self.display_text(e,
                        text = "Objects outside the viewport frame is not listed.",
                        size = RHINO_CONDUIT.ConduitTextSize.Normal)

        self.display_space()
        self.display_seperation_line(e)


        for layer in get_good_layers():
            objs = rs.VisibleObjects()
            obj = filter(lambda x: rs.ObjectLayer(x) == layer, objs)[0]
            my_color = rs.LayerColor(layer)

            center = RHINO_OBJ_DATA.get_center(obj)

            pt_on_screen = rs.XformWorldToScreen(center, screen_coordinates=False)
            pt_start = System.Drawing.Point(self.pointer_2d[0]+ 9 * len(layer), self.pointer_2d[1] + 15/2 )

            pt_kink = System.Drawing.Point(self.pointer_2d[0]+ 9 * len(layer) + 20, self.pointer_2d[1] + 15/2 )
            pt_end = System.Drawing.Point(pt_on_screen[0] , pt_on_screen[1])

            e.Display.Draw2dLine (pt_start, pt_kink, my_color, 1)
            e.Display.Draw2dLine (pt_end, pt_kink, my_color, 1)


            self.display_text(e,
                            text = RHINO_LAYER.rhino_layer_to_user_layer(layer),
                            size = RHINO_CONDUIT.ConduitTextSize.Normal,
                            color = my_color )


        self.reset_pointer(e)

def get_good_layers():

    objs = rs.VisibleObjects()
    layers = list(set([rs.ObjectLayer(x) for x in objs]))
    return sorted(layers)



def toggle_layer_pointer():

    if sc.sticky.has_key(KEY):
        conduit = sc.sticky[KEY]
    else:
        # create a conduit and place it in sticky
        conduit = LayerDisplayConduit()
        sc.sticky[KEY] = conduit

    # Toggle enabled state for conduit. Every time this script is
    # run, it will turn the conduit on and off
    conduit.Enabled = not conduit.Enabled
    if conduit.Enabled:
        print ("conduit enabled")
    else:
        print ("conduit disabled")

    sc.doc.Views.Redraw()
