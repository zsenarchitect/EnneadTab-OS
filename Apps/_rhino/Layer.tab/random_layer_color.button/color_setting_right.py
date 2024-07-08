
__title__ = "RandomLayerColorSetting"
__doc__ = "Change the setting of color style."

import rhinoscriptsyntax as rs
import sys
import os
script_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(script_folder)
import random_layer_color_left as RLC



from EnneadTab import DATA_FILE
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def color_setting():


    current_setting = RLC.get_current_setting()
    current_option = []
    for item in RLC.COLOR_SETTING_DEFAULT:
        title, _ = item
        current_option.append((title, current_setting[title]))
    res = rs.CheckListBox(current_option, "After changing setting, run randomizer again.","EnneadTab Random Layer Color Setting")

    setting = {}
    if not res:
        return
    for item in res:
        title, value = item
        setting[title] = value
        
        
    DATA_FILE.set_sticky_longterm(RLC.KEY_COLOR_SETTING, setting)



if __name__ == "__main__":
    color_setting()