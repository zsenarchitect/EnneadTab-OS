
import math
import sys
import os
import pyautogui


class BaseGUI:

    BACKGROUND_COLOR = (80, 97, 81)# new green
    BACKGROUND_COLOR = (52, 78, 91) # original blue
    TEXT_COLOR = (255, 255, 255)
    TEXT_COLOR_FADE = (150, 150, 150)
    TEXT_COLOR_WARNING = (252, 127, 3)
    TEXT_COLOR_BIG_WARNING = (242, 52, 39)

    
    FONT_TITLE = ("arialblack", 30)
    FONT_SUBTITLE = ("arialblack", 20)
    FONT_BODY = ("arial", 15)
    FONT_NOTE = ("arialblack", 10)

    run = True

    
                
    def is_another_app_running(self):
        if not hasattr(self, 'app_title'):
            return False
        for window in pyautogui.getAllWindows():
            if window.title == self.app_title:
                return True
        return False

 
