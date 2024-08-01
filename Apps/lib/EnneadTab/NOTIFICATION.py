#!/usr/bin/python
# -*- coding: utf-8 -*-

import SOUND
import DATA_FILE
import EXE
import IMAGE
import CONFIG

def is_hate_messenger():
    return not (CONFIG.get_setting("radio_bt_popup_standard", True) or CONFIG.get_setting("radio_bt_popup_full", True))

def is_hate_duck_pop():
    return not CONFIG.get_setting("toggle_bt_is_duck_allowed", True)

def messenger(main_text,
             width = 1200,
             height = None,
             image = None,
             animation_stay_duration = 5,
             x_offset = 0):
    """pop simple messag from bm of screen and disappear later. This can replace the WIN versino becasue it is 
    less annoying with sound.

    Args:
        main_text (str): the message to show. Better within 2 return lines. If too long, please use line return
        width (int, optional): how width is the message max width. Defaults to 1200.
        height (int, optional): how tall is the message max height. Defaults to 150.
    """

    if is_hate_messenger():
        return
    
    if not isinstance(main_text, str):
        main_text = str(main_text)

        

    data = {}
    data["main_text"] = main_text
    data["animation_in_duration"] = 0.5
    data["animation_stay_duration"] = animation_stay_duration
    data["animation_fade_duration"] = 2
    data["width"] = width
    data["height"] = height or 150 + str(main_text).count("\n") * 40
    data["image"] = image
    data["x_offset"] = x_offset

    DATA_FILE.set_data(data, "messenger_data.sexyDuck")



    EXE.try_open_app("Messenger")


def duck_pop(main_text = None):
    if is_hate_duck_pop():
        return
    
    if not main_text:
        main_text = "Quack!"

    data = {}
    data["main_text"] = main_text

    # when the ranking is ready, can progress to make better ranked duck
    data["duck_image"] = IMAGE.get_one_image_path_by_prefix("duck_pop")
    data["explosion_gif"] = IMAGE.get_image_path_by_name("duck_explosion.gif")
    data["audio"] = SOUND.get_one_audio_path_by_prefix("duck")
    DATA_FILE.set_data(data, "DUCK_POP.sexyDuck") 

    EXE.try_open_app("DuckPop", legacy_name="Duck_Pop")
  

def unit_test():
    duck_pop("Hello, Ennead!")
    messenger("Hello Ennead!")

if __name__ == "__main__":
    duck_pop("Hello, world!")
    messenger("Hello world")
