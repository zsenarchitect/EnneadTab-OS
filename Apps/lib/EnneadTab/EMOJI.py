#!/usr/bin/python
# -*- coding: utf-8 -*-


import FOLDER


def pick_emoji_text():
    import io
    with io.open('{}\\FUN\\_emoji_text.txt'.format(FOLDER.get_folder_path_from_path(__file__)), "r", encoding = "utf8") as f:
        lines = f.readlines()
    lines = [x.replace("\n", "") for x  in lines if x != "\n"]
    from pyrevit import forms
    sel = forms.SelectFromList.show(lines, select_multiple = False, title = "Go wild")
    if not sel:
        return

    forms.ask_for_string(default = sel,
                        prompt = 'Copy below text to anywhere, maybe SheetName or Schedule',
                        title = 'pick_emoji_text')


def random_emoji():
    import io
    with io.open('{}\\_emoji_text.txt'.format(FOLDER.get_folder_path_from_path(__file__)), "r", encoding = "utf8") as f:
        lines = f.readlines()
    lines = [x.replace("\n", "") for x  in lines if x != "\n"]
    import random
    
    random.shuffle(lines)
    return lines[0].replace("\n", "")
    