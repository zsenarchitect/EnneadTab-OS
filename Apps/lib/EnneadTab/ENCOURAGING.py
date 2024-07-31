#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import textwrap

import FOLDER
import NOTIFICATION
import CONFIG

def is_hate_encouraging():
    return not CONFIG.get_setting("radio_bt_popup_full", True)


def random_warming_quote():
    with open('{}\_warming_quotes.txt'.format(FOLDER.get_folder_path_from_path(__file__)), "r") as f:
        lines = f.readlines()
    random.shuffle(lines)
    return lines[0].replace("\n", "")


def warming_quote():
    quote = random_warming_quote()
    

    # Wrap this text.
    wrapper = textwrap.TextWrapper(width = 100)
    quote = wrapper.fill(text = quote)


    NOTIFICATION.messenger(main_text = quote, animation_stay_duration = 10)
