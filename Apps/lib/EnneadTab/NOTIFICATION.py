#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import os
import SOUND
import FOLDER
import DATA_FILE
import USER
import EXE
import ENVIRONMENT
import IMAGE





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




    # import random
    # if random.random() < 0.0001:
    #     if duck_pop(main_text):
    #         return
    
    if not isinstance(main_text, str):
        main_text = str(main_text)

        
    with DATA_FILE.update_data("MESSENGER.json") as data:
        
        data["main_text"] = main_text
        data["animation_in_duration"] = 0.5
        data["animation_stay_duration"] = animation_stay_duration
        data["animation_fade_duration"] = 2
        data["width"] = width
        data["height"] = height or 150 + str(main_text).count("\n") * 40
        data["image"] = image
        data["x_offset"] = x_offset




    EXE.try_open_app("Messenger")


def duck_pop(main_text = None):
    if not main_text:
        main_text = "Quack!"


    with DATA_FILE.update_data("DUCK_POP.json") as data:
        data["main_text"] = main_text
        data["duck_image"] = IMAGE.get_image_path_by_name("duck_green_bg.png")
        data["explosion_gif"] = IMAGE.get_image_path_by_name("duck_explosion.gif")
        data["audio"] = SOUND.get_one_audio_path_by_prefix("duck")

    EXE.try_open_app("Duck_Pop")
  



if __name__ == "__main__":
    duck_pop("Hello, world!")