#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT
import ENVIRONMENT
import COLOR

if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    import Eto # pyright: ignore






def apply_dark_style(UI):
    
    logo_dark_path = "{}\\bin\\images\\Ennead_Architects_Logo_DarkBackground.png".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)  
    temp_bitmap = Eto.Drawing.Bitmap(logo_dark_path)
    if hasattr(UI, "logo"):
        UI.logo.Image = temp_bitmap.WithSize(200,30)
    
    icon_path = "{}\\bin\\images\\Form Icon.png".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_RHINO)
    UI.Icon = Eto.Drawing.Icon(icon_path)
    
    
    apply_styles_to_control(UI.Content)

def apply_styles_to_control(control):

    
    if hasattr(control, "DataStore"):
        if isinstance(control, Eto.Forms.RadioButtonList):
            pass
        elif isinstance(control, Eto.Forms.CheckBoxList):
            pass
        else:
            return
    
    dark_background_color = Eto.Drawing.Color(70/256.0,70/256.0,70/256.0)
    light_dark_background_color = Eto.Drawing.Color(100/256.0,100/256.0,100/256.0)
    text_color = Eto.Drawing.Color(218/256.0,232/256.0,253/256.0)


    # Apply styles to buttons

    if isinstance(control, Eto. Forms.Button):
        control.BackgroundColor = dark_background_color
        control.TextColor = text_color


    # Apply styles to labels
    elif isinstance(control, Eto. Forms.Label):
        control.TextColor = text_color

    elif isinstance(control, Eto.Forms.TextBox):
        control.BackgroundColor = light_dark_background_color
        control.TextColor = text_color

    elif isinstance(control, Eto.Forms.RadioButtonList):
        control.BackgroundColor = dark_background_color
        control.TextColor = text_color
        
    elif isinstance(control, Eto.Forms.CheckBoxList):
        control.BackgroundColor = dark_background_color
        control.TextColor = text_color
    
    elif isinstance(control, Eto.Forms.GroupBox):
        control.BackgroundColor = dark_background_color
        control.TextColor = text_color
        
    # if isinstance(control, Eto.Forms.GridView):
    # #     print control.BackgroundColor
    #     control.CellFormatting += OnCellFormatting
        
    elif isinstance(control, Eto.Forms.DynamicLayout):
        control.BackgroundColor = dark_background_color
        
    elif isinstance(control, Eto.Forms.TableLayout):
        control.BackgroundColor = dark_background_color
        
    elif isinstance(control, Eto.Forms.StackLayout):
        control.BackgroundColor = dark_background_color

    # Check and replace image path for ImageView
    # elif isinstance(control, Eto.Forms.ImageView):
    #     #  and "Ennead_Architects_Logo" in control.Image.FileName
    #     print control.Image
    #     for x in dir(control.Image):
    #         print x
    #     temp_bitmap = Eto.Drawing.Bitmap(logo_dark_path)
    #     control.Image = temp_bitmap.WithSize(200,30)

    # Recursively apply styles to sub-controls
    if hasattr(control, "Controls"):
        for sub_control in control.Controls:
            apply_styles_to_control(sub_control)
    elif hasattr(control, "Items"):
        if isinstance(control, Eto.Forms.MenuItem):
            pass
        elif isinstance(control, Eto.Forms.ComboBox):
            pass
        else:
            for item in control.Items:
                apply_styles_to_control(item)


def OnCellFormatting(self, sender, e): 
    e.ForegroundColor = Eto.Drawing.Colors.White 

    if e.Row % 2 == 0:
        e.Cell.BackgroundColor = Eto.Drawing.Color(70/256.0,70/256.0,70/256.0)
    else:
        e.Cell.BackgroundColor = Eto.Drawing.Color(100/256.0,100/256.0,100/256.0)


def unit_test():
    pass

if __name__ == "__main__":
    unit_test()