__alias__ = "ToggleBlockColorDisplay_Setting"
__doc__ = "Toggle the on/off of block names."


import scriptcontext as sc

def display_setting():

    key = "EA_color_block_display_conduit_show_text"
    if not sc.sticky.has_key(key):
        sc.sticky[key] = False
    else:
        sc.sticky[key] = not sc.sticky[key]

    sc.doc.Views.Redraw()



