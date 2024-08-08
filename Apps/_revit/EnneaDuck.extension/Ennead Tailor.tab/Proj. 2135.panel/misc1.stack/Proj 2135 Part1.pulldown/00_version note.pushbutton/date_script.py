

__doc__ = "If 2135 toolset not working for you, restart you revit to receive current update"
__title__ = "Note: toolbar version 12.1"

from pyrevit import forms, DB, revit, script


################## main code below #####################
date = __title__.split("version ")[1]
output = script.get_output()
output.close_others()
print("Note: toolbar updated at {}, if 2135 toolset not working for you, restart you revit to receive current update".format(date))
