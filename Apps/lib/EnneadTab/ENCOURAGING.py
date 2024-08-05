#!/usr/bin/python
# -*- coding: utf-8 -*-
import io
import random
import textwrap

import FOLDER
import NOTIFICATION
import ENVIRONMENT
import CONFIG

def is_hate_encouraging():
    return not CONFIG.get_setting("radio_bt_popup_full", False)

def get_all_warming_quotes():
    with io.open('{}\\text\\_warming_quotes.txt'.format(ENVIRONMENT.DOCUMENT_FOLDER), "r", encoding = "utf8", errors="ignore") as f:
        lines = f.readlines()
    return [x.replace("\n", "") for x  in lines if x != "\n"]


def random_warming_quote():
    lines = get_all_warming_quotes()
    random.shuffle(lines)
    return lines[0].replace("\n", "")


def warming_quote():
    quote = random_warming_quote()
    

    # Wrap this text.
    wrapper = textwrap.TextWrapper(width = 100)
    quote = wrapper.fill(text = quote)


    NOTIFICATION.messenger(main_text = quote, animation_stay_duration = 10)
