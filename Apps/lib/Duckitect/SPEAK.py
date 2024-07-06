#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import DATA_FILE
import EXE
import CONFIG

def random_speak(lines, chance=1.0):
    if random.random() <= chance:
        random.shuffle(lines)
        speak(lines[0])


def is_hate_talkie():
    return not CONFIG.get_setting_data("toggle_bt_is_talkie", False)


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

    data = {}
    data["text"] = text
    data["language"] = language
    data["accent"] = accent
    DATA_FILE.set_data(data, "EA_Text2Speech.json")
    
 

    EXE.try_open_app("Speaker")


def unit_test():
    speak("I like to move it move it!")


if __name__ == "__main__":
    speak("This is a test?")