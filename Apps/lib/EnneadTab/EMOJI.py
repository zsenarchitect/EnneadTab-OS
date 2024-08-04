#!/usr/bin/python
# -*- coding: utf-8 -*-


import io
import random
import ENVIRONMENT

def get_all_emojis():
    with io.open('{}\\text\\_emoji_text.txt'.format(ENVIRONMENT.DOCUMENT_FOLDER), "r", encoding = "utf8") as f:
        lines = f.readlines()
    return [x.replace("\n", "") for x  in lines if x != "\n"]


def pick_emoji_text():

    lines = get_all_emojis()
    from pyrevit import forms
    sel = forms.SelectFromList.show(lines, select_multiple = False, title = "Go wild")
    if not sel:
        return

    forms.ask_for_string(default = sel,
                        prompt = 'Copy below text to anywhere, maybe SheetName or Schedule',
                        title = 'pick_emoji_text')


def random_emoji():
    lines = get_all_emojis()
    
    random.shuffle(lines)
    return lines[0].replace("\n", "")
    