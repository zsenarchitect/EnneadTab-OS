#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import DATA_FILE
import EXE
import CONFIGURE

def random_speak(lines, chance=1.0):
    if random.random() <= chance:
        random.shuffle(lines)
        speak(lines[0])


def is_hate_talkie():
    """
    file_name = 'revit_ui_setting.json'
    if not FOLDER.is_file_exist_in_dump_folder(file_name):
        return False


    setting_file = FOLDER.get_EA_dump_folder_file(file_name)
    data = DATA_FILE.read_json_as_dict(setting_file)
    return not data.get("toggle_bt_is_talkie", True)
    """
    return not CONFIGURE.get_setting_data("toggle_bt_is_talkie", True)


def speak(text, language='en', accent='com'):
    """
    #language = 'zh-CN'
    #language = 'zh-TW'
    #language = 'en'

    #accent = 'co.uk'
    #accent = 'co.in'
    #accent = 'com'
    """
    
    if not text:
        return

    with DATA_FILE.update_data("EA_Text2Speech.json") as data:
    
        data["text"] = text
        data["language"] = language
        data["accent"] = accent
 

    EXE.try_open_app("Speaker")