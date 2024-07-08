
#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import json

try:
    from System.Drawing import Color # pyright: ignore
    BLACK = Color.FromArgb(0,0,0)
    from colorsys import hsv_to_rgb, rgb_to_hsv
   
except:
    pass

# define before other custome import to avoid circular reference break in ironpython. 
# #cpython seem to be ok with this kind of circular ref
class TextColorEnum:
    Red = "red"
    Green = "green"
    Blue = "blue"
    Yellow = "yellow"
    Magenta = "magenta"
    Cyan = "cyan"
    White = "white"
ACCENT_COLOR = 70,70,70
PRIMARY_BACKGROUND = 100, 100, 100
PRIMARY_TEXT = 218,232,253


import ENVIRONMENT
if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
    from Autodesk.Revit.DB import Color as DB_Color # pyright: ignore
if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import Eto # pyright: ignore
import NOTIFICATION
import FOLDER







def from_rgb(r, g, b):
    """_summary_

    Args:
        r (_type_): _description_
        g (_type_): _description_
        b (_type_): _description_

    Returns:
        _type_: _description_
    """
    return Color.FromArgb(r, g, b)

def get_random_color(return_tuple = True):
    """get random color

    Returns:
       System.Drawing.Color: _description_
    """

    red = int(255*random.random())
    green = int(255*random.random())
    blue = int(255*random.random())


    color =  Color.FromArgb(red,green,blue)

    normalized_color = (color[0]/256.0, color[1]/256.0, color[2]/256.0)
    hsv_color = rgb_to_hsv(*normalized_color)
    grayed_hsv_color = (hsv_color[0], 0.6, hsv_color[2])
    grayed_rgb_color = hsv_to_rgb(*grayed_hsv_color)
    denormalized_rgb_color = (int(grayed_rgb_color[0]*256), int(grayed_rgb_color[1]*256), int(grayed_rgb_color[2]*256))

    if return_tuple:
        return denormalized_rgb_color
    return Color.FromArgb(*denormalized_rgb_color)

def tuple_to_color(tuple):
    """quickly convert 3 int to color object

    Args:
        tuple (tuple of 3 int): _description_

    Returns:
        System.Drawing.Color: _description_
    """
    red,green,blue = tuple
    
    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return DB_Color(red,green,blue)
    if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
        
        Eto.Drawing.Color(red/256.0,
                        green/256.0,
                        blue/256.0)
    
    return Color.FromArgb(red,green,blue)


def invert_color(color, return_tuple = False):
    """_summary_

    Args:
        color (_type_): _description_
        return_tuple (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    R, G, B = color[0], color[1], color[2]
    inverted_color = 255 - R, 255 - G, 255 - B
    if return_tuple:
        return inverted_color
    else:
        return Color.FromArgb(*inverted_color)
    
def rgb_to_hex(rgb_tuple):
    """convert rgb to hex

    Args:
        rgb (tuple): _description_

    Returns:
        str: _description_
    """
    return '#{:02x}{:02x}{:02x}'.format(int(rgb_tuple[0]),int(rgb_tuple[1]),int(rgb_tuple[2]))


def hex_to_rgb(hex_str):
    """convert hex to rgb

    Args:
        hex_str (str): _description_

    Returns:
        tuple: _description_
    """
    return tuple(int(str(hex_str).lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def decimal_to_rgb(decimal_color):
    red = decimal_color % 256
    green = (decimal_color // 256) % 256
    blue = (decimal_color // 256 // 256) % 256
    return (int(red), int(green), int(blue))



def is_same_color(color1, color2):
    """check if two color is same

    Args:
        color1 (tuple): _description_
        color2 (tuple): _description_

    Returns:
        bool: _description_
    """
    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return color1.Red == color2.Red and color1.Green == color2.Green and color1.Blue == color2.Blue
    

    return color1[0] == color2[0] and color1[1] == color2[1] and color1[2] == color2[2]




def _gather_data(raw_data, key_column):
    temp_data = {}
    for pointer in raw_data:
        i,j = pointer # i = row, j = column
        if j != key_column: 
            continue
        
        if i <=2:
            # ignore first two row, those rowsa re reserved for notes and header
            continue
        
        
        pointer_right_right = (i, j+2)
        subject_color = raw_data[pointer_right_right].get("color")
        
        # skip row where color is not defined(maybe due to merged cell), only record by row that define.
        if subject_color is None:
            continue
        
        
        
        subject = raw_data[pointer].get("value")
        if subject in [""]:
            continue
        
        pointer_right = (i, j+1)
        subject_abbr = raw_data[pointer_right].get("value")
        
        # if no abbr(maybe due to merged cell), use subject name as abbr. 
        subject_abbr = subject if subject_abbr == "" else subject_abbr
                                                       
        temp_data[subject] = {"abbr": subject_abbr, "color": subject_color}
        
    return temp_data
            
def get_color_template_data(template = None):
    if template:
        safe_template = FOLDER.copy_file_to_local_dump_folder(template)
    else:
        safe_template = "OFFICE STANDARD FILE TO BE MADE"
    
    if safe_template.endswith(".json"):
        with open(safe_template, "r") as f:
            return json.load(f)
        
    if safe_template.endswith(".xlsx"):
        NOTIFICATION.messenger(main_text="Please save as .xls instead of .xlsx")
        return {}
    
    
    if safe_template.endswith(".xls"):
        import EXCEL
        raw_data = EXCEL.read_data_from_excel(safe_template, 
                                                worksheet = "HEALTHCARE", 
                                                return_dict=True)

        
        #column A and D are 0, 3 for key column
        department_data = _gather_data(raw_data, key_column = 0)
        program_data = _gather_data(raw_data, key_column = 3)
       
            
        return {"department_color_map": department_data, "program_color_map": program_data}
