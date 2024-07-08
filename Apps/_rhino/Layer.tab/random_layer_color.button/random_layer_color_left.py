
__title__ = "RandomLayerColor"
__doc__ = "Randomize the layer color."


import rhinoscriptsyntax as rs
import random
from EnneadTab import SOUNDS
from EnneadTab import DATA_FILE
from EnneadTab import COLOR

KEY_COLOR_SETTING = "EA_RANDOM_LAYER_COLOR_SETTING"
COLOR_SETTING_DEFAULT = [("Change Pure Black", True), 
                        ("Change Pure White", True),
                        ("Change ANY other color with same RGB value", False)]


def random_layer_color(default_opt = False):
    options = ["Desaturated Colors", "Full RGB"]
    use_desaturated_color = True
    if default_opt == False:
        color_options = rs.ListBox(items = options, message= "select color option from below, only uncolored layer(default black) will be modified.\n\nKeyword for hue suggestion.\n\t'glass' and 'water' as blue hue.\n\t'grass' as green hue.", title = "random layer color", default = options[0])
        if color_options == options[1]:
            use_desaturated_color = False




    current_setting = get_current_setting()
    def should_process(color):
        r, g, b = color[0],color[1],color[2]
        if r == 0 and g == 0 and b == 0:
            return current_setting.get(COLOR_SETTING_DEFAULT[0][0], False)
        if r == 255 and g == 255 and b == 255:
            return current_setting.get(COLOR_SETTING_DEFAULT[1][0], False)
        if r == g == b:
            return current_setting.get(COLOR_SETTING_DEFAULT[2][0], False)
        return False
        
        
    all_layer_names = rs.LayerNames()
    for layer in all_layer_names:
        current_color = rs.LayerColor(layer)
        #print current_color
       
        
        if not should_process(current_color):
            continue
        
        rs.LayerColor(layer, color = random_color(layer, use_desaturated_color))
        """
        if str(current_color) == "Color [A=255, R=0, G=0, B=0]":
            rs.LayerColor(layer, color = random_color(layer, use_desaturated_color))
        """
    SOUNDS.play_sound(file = "sound effect_spray paint can shake_spray.wav")



def get_default_setting():  
    default_setting = {}
    for item in COLOR_SETTING_DEFAULT:
        title, value = item
        default_setting[title] = value
        
    return default_setting


def get_current_setting():
    current_setting = DATA_FILE.get_sticky_longterm(KEY_COLOR_SETTING, get_default_setting())
    return current_setting

def random_color(layer_name, use_desaturated_color):



    layer_name = layer_name.lower()

    def reduce():
        return int(255*random.random() * 0.1)
    def strong():
        return int(50*random.random()) + 200

    if "glass" in layer_name:
        red = reduce()
        green = reduce()
        blue = strong()
    elif "grass" in layer_name:
        red = reduce()
        green = strong()
        blue = reduce()
    elif "water" in layer_name or "pool" in layer_name:
        red = reduce()
        green = reduce()
        blue = strong()
    else:
        red = int(255*random.random())
        green = int(255*random.random())
        blue = int(255*random.random())


    color =  COLOR.from_rgb(red,green,blue)
    if not use_desaturated_color:
        return color
    #return color

    normalized_color = (color[0]/256.0, color[1]/256.0, color[2]/256.0)

    hsv_color = COLOR.rgb_to_hsv(*normalized_color)
    grayed_hsv_color = (hsv_color[0], 0.6, hsv_color[2])
    grayed_rgb_color = COLOR.hsv_to_rgb(*grayed_hsv_color) 
    denormalized_rgb_color = (int(grayed_rgb_color[0]*256), int(grayed_rgb_color[1]*256), int(grayed_rgb_color[2]*256))

    return denormalized_rgb_color


