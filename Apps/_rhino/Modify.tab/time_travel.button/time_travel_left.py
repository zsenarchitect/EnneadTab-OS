
__title__ = "TimeTravel"
__doc__ = "This button does TimeTravel when left click"
import rhinoscriptsyntax as rs
from EnneadTab import NOTIFICATION

def time_travel():
    if len(rs.SelectedObjects()) == 0:
        NOTIFICATION.toast(sub_text = "Time travel begin!",
                                    main_text = "Select objects to go back in time.")
    rs.Command("_UndoSelected")
