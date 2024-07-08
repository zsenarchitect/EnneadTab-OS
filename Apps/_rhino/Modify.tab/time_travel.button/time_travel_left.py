
__title__ = "TimeTravel"
__doc__ = "This button does TimeTravel when left click"
import rhinoscriptsyntax as rs
from EnneadTab import NOTIFICATION
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def time_travel():
    if len(rs.SelectedObjects()) == 0:
        NOTIFICATION.toast(sub_text = "Time travel begin!",
                                    main_text = "Select objects to go back in time.")
    rs.Command("_UndoSelected")




if __name__ == "__main__":
    time_travel()